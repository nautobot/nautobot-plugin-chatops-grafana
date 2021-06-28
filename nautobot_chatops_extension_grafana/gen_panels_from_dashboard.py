import json
import yaml

with open("django1.json", "r") as dashboard_file:
    dashboard_def = json.load(dashboard_file)

    dashboard_slug = "a-django-prometheus"
    dashboard_uid = dashboard_def["uid"]

    gen_panels_yml = []

    for panel in dashboard_def["panels"]:
        if panel.get("type", str()):
            if panel["type"] == "row":
                continue
            command_name = str("-".join(panel["title"].lower().split(" ")))
            panel_id = int(panel["id"])
            friendly_name = str(panel["title"])
            panel = {"command_name": f"{command_name}", "panel_id": panel_id, "friendly_name": f"{friendly_name}"}

        gen_panels_yml.append(panel)

    output = [{"dashboard_slug": f"{dashboard_slug}", "dashboard_uid": f"{dashboard_uid}", "panels": gen_panels_yml}]

    print(yaml.dump(output))
