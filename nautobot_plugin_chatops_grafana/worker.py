"""Worker function for /net commands in Slack."""
import logging
import tempfile
import argparse
import os
from datetime import datetime
from isodate import ISO8601Error, parse_duration
from jinja2 import Template
from django.conf import settings
from django_rq import job
from pydantic.error_wrappers import ValidationError  # pylint: disable=no-name-in-module
from nautobot.dcim import models
from nautobot_chatops.workers import handle_subcommands, add_subcommand
from .grafana import GrafanaHandler

logger = logging.getLogger("nautobot.plugin.grafana")

TIMEOUT = "60"
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_plugin_chatops_grafana"]
GRAFANA_LOGO_PATH = "grafana/grafana_icon.png"
GRAFANA_LOGO_ALT = "Grafana Logo"

_GRAFANA_HANDLER = None


def grafana_logo(dispatcher):
    """Construct an image_element containing the locally hosted Grafana logo."""
    return dispatcher.image_element(dispatcher.static_url(GRAFANA_LOGO_PATH), alt_text=GRAFANA_LOGO_ALT)


@job("default")
def grafana(subcommand, **kwargs):
    """Pull Panels from Grafana."""
    global _GRAFANA_HANDLER  # pylint: disable=global-statement
    _GRAFANA_HANDLER = GrafanaHandler(PLUGIN_SETTINGS)
    initialize_subcommands()
    _GRAFANA_HANDLER.set_current_subcommand(subcommand)
    return handle_subcommands("grafana", subcommand, **kwargs)


def initialize_subcommands():
    """Based on the panels configuration yaml provided build chat subcommands."""
    global _GRAFANA_HANDLER  # pylint: disable=global-statement
    raw_panels = _GRAFANA_HANDLER.get_panels()
    default_params = [
        f"width={_GRAFANA_HANDLER.get_width()}",
        f"height={_GRAFANA_HANDLER.get_height()}",
        f"theme={_GRAFANA_HANDLER.get_theme()}",
        f"timespan={_GRAFANA_HANDLER.get_timespan()}",
        f"timezone={_GRAFANA_HANDLER.get_timezone()}",
    ]
    for dashboard in raw_panels["dashboards"]:
        for panel in dashboard["panels"]:
            panel_variables = []
            # Build parameters list from dynamic variables in panels
            for variable in panel.get("variables", []):
                if variable.get("includeincmd", True):
                    panel_variables.append(variable["name"])
            # The subcommand name with be get-{command_name}
            add_subcommand(
                command_name="grafana",
                command_func=grafana,
                subcommand_name=f"get-{panel['command_name']}",
                subcommand_spec={
                    "worker": chat_get_panel,
                    "params": panel_variables + default_params,
                    "doc": panel["friendly_name"],
                },
            )


def chat_get_panel(dispatcher, *args) -> bool:
    """High level function to handle the panel request."""
    panel, parsed_args, dashboard_slug = chat_parse_args(dispatcher, *args)
    if not parsed_args:
        return False
    if not chat_validate_args(dispatcher, panel, parsed_args, *args):
        return False
    return chat_return_panel(dispatcher, panel, parsed_args, dashboard_slug)


def chat_parse_args(dispatcher, *args):
    """Parse the arguments from the user via chat using argparser.

    Returns:
        panel: dict the panel dict from the configuration file
        parsed_args: dict of the arguments from the user's raw input
        current_subcommand: str the name of the subcommane
        dashboard_slug: str the dashboard slug
    """
    global _GRAFANA_HANDLER  # pylint: disable=global-statement
    raw_panels = _GRAFANA_HANDLER.get_panels()
    current_subcommand = _GRAFANA_HANDLER.get_current_subcommand()
    dashboard_slug = None
    panel = None

    # Find the panel config matching the current subcommand
    for dashboard in raw_panels["dashboards"]:
        panel = next((i for i in dashboard["panels"] if f"get-{i['command_name']}" == current_subcommand), None)
        if panel:
            dashboard_slug = dashboard["dashboard_slug"]
            break

    if not panel:
        dispatcher.send_error(f"Command {current_subcommand} Not Found!")
        return False

    args = [f"--{arg}" for arg in args if not arg.startswith("--")]

    # Collect the arguments sent by the user parse them matching the panel config
    parser = argparse.ArgumentParser(description="Handles command arguments")
    predefined_args = {}
    for variable in panel.get("variables", []):
        if variable.get("includeincmd", True):
            parser.add_argument(f"--{variable['name']}", default=variable.get("response", ""), nargs="?")
        else:
            # The variable from the config wasn't included in the users response (hidden) so
            # ass the default response if provided in the config
            predefined_args[variable["name"]] = variable.get("response", "")
    parser.add_argument("--width", default=_GRAFANA_HANDLER.get_width(), nargs="?")
    parser.add_argument("--height", default=_GRAFANA_HANDLER.get_height(), nargs="?")
    parser.add_argument("--theme", default=_GRAFANA_HANDLER.get_theme(), nargs="?")
    parser.add_argument("--timespan", default=_GRAFANA_HANDLER.get_timespan(), nargs="?")
    parser.add_argument("--timezone", default=_GRAFANA_HANDLER.get_timezone(), nargs="?")
    args_namespace = parser.parse_args(args)
    parsed_args = {**vars(args_namespace), **predefined_args}
    return panel, parsed_args, dashboard_slug


def chat_validate_args(dispatcher, panel, parsed_args, *args):  # pylint: disable=too-many-return-statements
    """Validate all arguments from the chatbot."""
    global _GRAFANA_HANDLER  # pylint: disable=global-statement
    current_subcommand = _GRAFANA_HANDLER.get_current_subcommand()

    # Validate nautobot Args and get any missing parameters
    if not chat_validate_nautobot_args(
        dispatcher=dispatcher,
        panel=panel,
        parsed_args=parsed_args,
        action_id=f"grafana {current_subcommand} {' '.join(args)}",
        helper_prefix=f"{panel['friendly_name']}",
    ):
        return False

    # Validate and set any additional args
    try:
        _GRAFANA_HANDLER.set_width(parsed_args["width"])
    except ValidationError:
        dispatcher.send_error(f"{parsed_args['width']} Is and invalid width please enter an integer.")
        return False

    try:
        _GRAFANA_HANDLER.set_height(parsed_args["height"])
    except ValidationError:
        dispatcher.send_error(f"{parsed_args['height']} Is an invalid height, please enter an integer.")
        return False

    try:
        _GRAFANA_HANDLER.set_theme(parsed_args["theme"])
    except ValidationError:
        dispatcher.send_error(f"{parsed_args['theme']} Is an invalid theme, please choose light or dark.")
        return False

    try:
        _GRAFANA_HANDLER.set_timespan(parsed_args["timespan"])
    except ValidationError:
        dispatcher.send_error(
            f"{parsed_args['timespan']} Is an invalid timedelta, "
            f"please see https://en.wikipedia.org/wiki/ISO_8601#Durations for more information"
        )
        return False
    except ISO8601Error:
        dispatcher.send_error(
            f"{parsed_args['timespan']} Is an invalid timespan (e.g. 'P12M' for the past 12 months), "
            f"please see https://en.wikipedia.org/wiki/ISO_8601#Durations for more information"
        )
        return False

    try:
        _GRAFANA_HANDLER.set_timezone(parsed_args["timezone"])
    except ValidationError:
        dispatcher.send_error(f"{parsed_args['theme']} Is an invalid timezone.")
        return False

    return True


def chat_return_panel(dispatcher, panel, parsed_args, dashboard_slug):
    """After everything passes the tests decorate the response and return the panel to the user."""
    global _GRAFANA_HANDLER  # pylint: disable=global-statement
    current_subcommand = _GRAFANA_HANDLER.get_current_subcommand()

    dispatcher.send_markdown(
        f"Standby {dispatcher.user_mention()}, I'm getting that result.\n"
        f"Please be patient as this can take up to {TIMEOUT} seconds.",
        ephemeral=True,
    )
    dispatcher.send_busy_indicator()

    raw_png = _GRAFANA_HANDLER.get_png(dashboard_slug, panel)
    if not raw_png:
        dispatcher.send_error("An error occurred while accessing Grafana")
        return False

    chat_header_args = []
    for variable in panel.get("variables", []):
        if variable.get("includeincmd", True):
            chat_header_args += [(variable.get("friendly_name", variable["name"]), str(parsed_args[variable["name"]]))]
    dispatcher.send_blocks(
        dispatcher.command_response_header(
            "grafana",
            current_subcommand,
            chat_header_args[:5],
            panel["friendly_name"],
            grafana_logo(dispatcher),
        )
    )

    with tempfile.TemporaryDirectory() as tempdir:
        # Note: Microsoft Teams will silently fail if we have ":" in our filename.
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d-%H-%M-%S")

        # If a timespan is specified, set the filename of the image to be the correct timespan displayed in the
        # Grafana image.
        if parsed_args.get("timespan"):
            timedelta = parse_duration(parsed_args.get("timespan")).totimedelta(start=now)
            from_ts = (now - timedelta).strftime("%Y-%m-%d-%H-%M-%S")
            time_str = f"{from_ts}-to-{time_str}"

        img_path = os.path.join(tempdir, f"{current_subcommand}_{time_str}.png")
        with open(img_path, "wb") as img_file:
            img_file.write(raw_png)
        dispatcher.send_image(img_path)
    return True


def chat_validate_nautobot_args(  # pylint: disable=too-many-locals
    dispatcher, panel, parsed_args, action_id, helper_prefix
) -> bool:
    """Parse through args and validate them against the definition with the panel."""
    validated_variables = {}
    print(panel.get("variables", []))
    for variable in panel.get("variables", []):
        if not variable.get("query", False):
            logger.debug("Validated Variable %s with input %s", variable["name"], parsed_args[variable["name"]])
            validated_variables[variable["name"]] = parsed_args[variable["name"]]

        print("Validating Variable %s with input %s", variable["name"], parsed_args[variable["name"]])
        logger.debug("Validating Variable %s with input %s", variable["name"], parsed_args[variable["name"]])
        # A nautobot Query is defined so first lets get all of those objects
        try:
            model = getattr(models, variable["query"])
            objects = model.objects.all()
        except Exception as err:  # pylint: disable=broad-except
            logger.error("Unable to find class %s in dcim.models: %s", variable["query"], err)
            dispatcher.send_error(
                f"Sorry, {dispatcher.user_mention()} there was an error with your panel definition, "
                f"I was unable to find class {variable['query']} in dcim.models"
            )
            return False
        if not variable.get("modelattr", False):
            dispatcher.send_error(
                f"Sorry, {dispatcher.user_mention()} there was an error with your panel definition, "
                f"When specifying a query, a modelattr is also required"
            )
            return False
        if objects.count() < 1:
            dispatcher.send_error(
                f"Sorry, {dispatcher.user_mention()}, your query for"
                f" {variable['query']} returned {objects.count()}."
            )
            return False

        # Now lets validate the object and prompt the user for a correct object
        object_filter = variable.get("filter", {})
        if parsed_args[variable["name"]] and parsed_args[variable["name"]] != "":
            object_filter[variable["modelattr"]] = parsed_args[variable["name"]]

        # Parse Jinja in filter
        for filter_key in object_filter.keys():
            template = Template(object_filter[filter_key])
            object_filter[filter_key] = template.render(validated_variables)

        try:
            filtered_objects = objects.filter(**object_filter)
        except Exception:  # pylint: disable=broad-except
            logger.error("Unable to filter %s by %s", variable["query"], object_filter)
            dispatcher.send_error(
                f"Sorry, {dispatcher.user_mention()} there was an error with your panel definition, "
                f"I was unable to filter {variable['query']} by {object_filter}"
            )
            return False
        if filtered_objects.count() != 1:
            # dispatcher.send_error(
            #     f"Sorry, {dispatcher.user_mention()}, your query for {variable['query']} "
            #     f"filtering by {object_filter} returned {filtered_objects.count()} it must return exactly 1"
            # )
            if filtered_objects.count() > 1:
                choices = [
                    (f"{filtered_object.name}", getattr(filtered_object, variable["modelattr"]))
                    for filtered_object in filtered_objects
                ]
            else:
                choices = [(f"{obj.name}", getattr(obj, variable["modelattr"])) for obj in objects]
            helper_text = (
                f"{helper_prefix} Requires {variable['friendly_name']}"
                if variable.get("friendly_name", False)
                else helper_prefix
            )
            parsed_args[variable["name"]] = dispatcher.prompt_from_menu(action_id, helper_text, choices)
            return False
        # Add the validated device to the dict so templates can use it later
        logger.debug("Validated Variable %s with input %s", variable["name"], parsed_args[variable["name"]])
        validated_variables[variable["name"]] = filtered_objects[0].__dict__

        # Now we now we have a valid device lets parse the value template for this variable
        template = Template(variable.get("value", str(validated_variables[variable["name"]])))
        variable["value"] = template.render(validated_variables)
    return True
