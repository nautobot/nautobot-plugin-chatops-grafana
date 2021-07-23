"""Django table classes for Nautobot."""

from django_tables2 import TemplateColumn
from nautobot.utilities.tables import BaseTable, ToggleColumn, ButtonsColumn
from nautobot_plugin_chatops_grafana.models import Panel, Dashboard, PanelVariable


def _action_template(view: str) -> str:
    return f"""
<a  href="{{% url 'plugins:nautobot_plugin_chatops_grafana:{view}_changelog' pk=record.pk %}}"
    class="btn btn-default btn-xs" title="Change log">
        <span class="mdi mdi-history"></span>
</a>

<a  href="{{% url 'plugins:nautobot_plugin_chatops_grafana:{view}_update' pk=record.pk %}}"
    class="btn btn-xs btn-warning">
        <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
</a>

<a  href="{{% url 'plugins:nautobot_plugin_chatops_grafana:{view}_delete' pk=record.pk %}}"
    class="btn btn-xs btn-danger">
        <i class="mdi mdi-trash-can-outline" aria-hidden="true"></i>
</a>"""


class DashboardViewTable(BaseTable):
    """Table for rendering panels for dashboards in the grafana plugin."""

    pk = ToggleColumn()

    actions = ButtonsColumn(Dashboard, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta for class DashboardViewTable."""

        model = Dashboard
        fields = ("pk", "dashboard_slug", "dashboard_uid", "friendly_name", "actions")


class PanelViewTable(BaseTable):
    """Table for rendering panels for dashboards in the grafana plugin."""

    pk = ToggleColumn()

    actions = ButtonsColumn(Panel, buttons=("changelog", "edit", "delete"))

    chat_command = TemplateColumn(
        template_code="<span class='text-muted'><i>/grafana get-{{ record.command_name }}</i></span>",
        verbose_name="Chat Command",
    )

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta for class PanelViewTable."""

        model = Panel
        fields = ("pk", "chat_command", "command_name", "friendly_name", "panel_id", "dashboard", "actions")


class PanelVariableViewTable(BaseTable):
    """Table for rendering panel variables for dashboards in the grafana plugin."""

    pk = ToggleColumn()

    actions = ButtonsColumn(PanelVariable, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta for class PanelVariableViewTable."""

        model = PanelVariable
        fields = tuple(["pk"] + PanelVariable.csv_headers + ["actions"])
