"""Worker function for /net commands in Slack."""
import logging
import tempfile
import argparse
import os
from datetime import datetime
from isodate import ISO8601Error, parse_duration
from jinja2 import Template
from django_rq import job
from django.core.exceptions import FieldError
from pydantic.error_wrappers import ValidationError  # pylint: disable=no-name-in-module
from nautobot.dcim import models
from nautobot_chatops.workers import handle_subcommands, add_subcommand
from .grafana import SLASH_COMMAND, handler

logger = logging.getLogger("nautobot.plugin.grafana")

TIMEOUT = "60"
GRAFANA_LOGO_PATH = "grafana/grafana_icon.png"
GRAFANA_LOGO_ALT = "Grafana Logo"


def grafana_logo(dispatcher):
    """Construct an image_element containing the locally hosted Grafana logo."""
    return dispatcher.image_element(dispatcher.static_url(GRAFANA_LOGO_PATH), alt_text=GRAFANA_LOGO_ALT)


@job("default")
def grafana(subcommand, **kwargs):
    """Pull Panels from Grafana."""
    initialize_subcommands()
    handler.current_subcommand = subcommand
    return handle_subcommands(SLASH_COMMAND, subcommand, **kwargs)


def initialize_subcommands():
    """Based on the panels configuration yaml provided build chat subcommands."""
    raw_panels = handler.panels
    default_params = [
        f"width={handler.width}",
        f"height={handler.height}",
        f"theme={handler.theme}",
        f"timespan={handler.timespan}",
        f"timezone={handler.timezone}",
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
                command_name=SLASH_COMMAND,
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
    raw_panels = handler.panels
    dashboard_slug = None
    panel = None

    # Find the panel config matching the current subcommand
    for dashboard in raw_panels["dashboards"]:
        panel = next((i for i in dashboard["panels"] if f"get-{i['command_name']}" == handler.current_subcommand), None)
        if panel:
            dashboard_slug = dashboard["dashboard_slug"]
            break

    if not panel:
        dispatcher.send_error(f"Command {handler.current_subcommand} Not Found!")
        return False

    # Append on the flag command to conform to argparse parsing methods.
    fixed_args = []
    for arg in args:
        if arg.startswith(handler.default_params):
            fixed_args.append(f"--{arg}")
        else:
            fixed_args.append(arg)

    # Collect the arguments sent by the user parse them matching the panel config
    parser = argparse.ArgumentParser(description="Handles command arguments")
    predefined_args = {}
    for variable in panel.get("variables", []):
        if variable.get("includeincmd", True):
            parser.add_argument(f"{variable['name']}", default=variable.get("response", ""), nargs="?")
        else:
            # The variable from the config wasn't included in the users response (hidden) so
            # ass the default response if provided in the config
            predefined_args[variable["name"]] = variable.get("response", "")

    parser.add_argument("--width", default=handler.width, nargs="?")
    parser.add_argument("--height", default=handler.height, nargs="?")
    parser.add_argument("--theme", default=handler.theme, nargs="?")
    parser.add_argument("--timespan", default=handler.timespan, nargs="?")
    parser.add_argument("--timezone", default=handler.timezone, nargs="?")
    args_namespace = parser.parse_args(fixed_args)
    parsed_args = {**vars(args_namespace), **predefined_args}
    return panel, parsed_args, dashboard_slug


def chat_validate_args(dispatcher, panel, parsed_args, *args):  # pylint: disable=too-many-return-statements
    """Validate all arguments from the chatbot."""
    # Validate nautobot Args and get any missing parameters
    try:
        chat_validate_nautobot_args(
            dispatcher=dispatcher,
            panel=panel,
            parsed_args=parsed_args,
            action_id=f"grafana {handler.current_subcommand} {' '.join(args)}",
        )
    except PanelArgsError as exc:
        dispatcher.send_error(f"Sorry, {dispatcher.user_mention()} there was an error with the panel definition, {exc}")
        return False

    except ArgsError as exc:
        dispatcher.send_error(exc)
        return False

    except MultipleOptionsError:
        return False

    return True


class ArgsError(BaseException):
    pass


class PanelArgsError(BaseException):
    pass


class MultipleOptionsError(BaseException):
    pass


def chat_return_panel(dispatcher, panel, parsed_args, dashboard_slug):
    """After everything passes the tests decorate the response and return the panel to the user."""

    dispatcher.send_markdown(
        f"Standby {dispatcher.user_mention()}, I'm getting that result.\n"
        f"Please be patient as this can take up to {TIMEOUT} seconds.",
        ephemeral=True,
    )
    dispatcher.send_busy_indicator()

    raw_png = handler.get_png(dashboard_slug, panel)
    if not raw_png:
        dispatcher.send_error("An error occurred while accessing Grafana")
        return False

    chat_header_args = []
    for variable in panel.get("variables", []):
        if variable.get("includeincmd", True):
            chat_header_args.append(
                (variable.get("friendly_name", variable["name"]), str(parsed_args[variable["name"]]))
            )
    dispatcher.send_blocks(
        dispatcher.command_response_header(
            SLASH_COMMAND,
            handler.current_subcommand,
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

        img_path = os.path.join(tempdir, f"{handler.current_subcommand}_{time_str}.png")
        with open(img_path, "wb") as img_file:
            img_file.write(raw_png)
        dispatcher.send_image(img_path)
    return True


def chat_validate_nautobot_args(dispatcher, panel, parsed_args, action_id):  # pylint: disable=too-many-locals
    """Parse through args and validate them against the definition with the panel."""
    validated_variables = {}

    for variable in panel.get("variables", []):
        if not variable.get("query", False):
            logger.debug("Validated Variable %s with input %s", variable["name"], parsed_args[variable["name"]])
            validated_variables[variable["name"]] = parsed_args[variable["name"]]
        else:
            print(f"Validating Variable {variable['name']} with input {parsed_args[variable['name']]}")
            logger.debug("Validating Variable %s with input %s", variable["name"], parsed_args[variable["name"]])
            # A nautobot Query is defined so first lets get all of those objects
            try:
                # Example, if a 'query' defined in panels.yml is set to 'Site', we would pull all sites
                # using 'Site.objects.all()'
                objects = getattr(models, variable["query"]).objects.all()
            except AttributeError as exc:
                logger.error("Unable to find class %s in dcim.models: %s", variable["query"], exc)
                raise PanelArgsError(f"I was unable to find class {variable['query']} in dcim.models")

            if not variable.get("modelattr", False):
                raise PanelArgsError(f"When specifying a query, a modelattr is also required")
            if objects.count() < 1:
                raise PanelArgsError(f"{variable['query']} returned {objects.count()} items in the dcim.model.")

            # Now lets validate the object and prompt the user for a correct object
            object_filter = variable.get("filter", {})
            if parsed_args.get(variable["name"], "") != "":
                object_filter[variable["modelattr"]] = parsed_args[variable["name"]]

            # Parse Jinja in filter
            for filter_key in object_filter.keys():
                template = Template(object_filter[filter_key])
                object_filter[filter_key] = template.render(validated_variables)

            try:
                filtered_objects = objects.filter(**object_filter)
            except FieldError:
                logger.error("Unable to filter %s by %s", variable["query"], object_filter)
                raise PanelArgsError(f"I was unable to filter {variable['query']} by {object_filter}") from None

            if filtered_objects.count() != 1:
                if filtered_objects.count() > 1:
                    choices = [
                        (f"{filtered_object.name}", getattr(filtered_object, variable["modelattr"]))
                        for filtered_object in filtered_objects
                    ]
                else:
                    choices = [(f"{obj.name}", getattr(obj, variable["modelattr"])) for obj in objects]
                helper_text = (
                    f"{panel['friendly_name']} Requires {variable['friendly_name']}"
                    if variable.get("friendly_name", False)
                    else panel["friendly_name"]
                )
                parsed_args[variable["name"]] = dispatcher.prompt_from_menu(action_id, helper_text, choices)
                raise MultipleOptionsError

            # Add the validated device to the dict so templates can use it later
            logger.debug("Validated variable %s with input %s", variable["name"], parsed_args[variable["name"]])
            validated_variables[variable["name"]] = filtered_objects[0].__dict__

        # Now we now we have a valid device lets parse the value template for this variable
        template = Template(variable.get("value", str(validated_variables[variable["name"]])))
        variable["value"] = template.render(validated_variables)

        # Validate and set any additional args
        try:
            handler.width = parsed_args["width"]
        except ValidationError as exc:
            raise ArgsError(f"{parsed_args['width']} Is and invalid width please enter an integer.") from None

        try:
            handler.height = parsed_args["height"]
        except ValidationError:
            raise ArgsError(f"{parsed_args['height']} Is an invalid height, please enter an integer.") from None

        try:
            handler.theme = parsed_args["theme"]
        except ValidationError:
            raise ArgsError(f"{parsed_args['theme']} Is an invalid theme, please choose light or dark.") from None

        try:
            handler.timespan = parsed_args["timespan"]
        except ValidationError:
            raise ArgsError(
                f"{parsed_args['timespan']} Is an invalid timedelta, "
                f"please see https://en.wikipedia.org/wiki/ISO_8601#Durations for more information"
            ) from None
        except ISO8601Error:
            raise ArgsError(
                f"{parsed_args['timespan']} Is an invalid timespan (e.g. 'P12M' for the past 12 months), "
                f"please see https://en.wikipedia.org/wiki/ISO_8601#Durations for more information"
            ) from None

        try:
            handler.timezone = parsed_args["timezone"]
        except ValidationError:
            raise ArgsError(f"{parsed_args['theme']} Is an invalid timezone.") from None
