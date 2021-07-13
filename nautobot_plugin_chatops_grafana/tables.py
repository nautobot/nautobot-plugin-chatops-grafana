"""Django table classes for Nautobot."""

from django_tables2 import TemplateColumn
from nautobot.utilities.tables import BaseTable
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

    actions = TemplateColumn(
        template_code=_action_template("dashboards"),
        attrs={"td": {"class": "text-right noprint"}},
        verbose_name="",
    )

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta for class DashboardViewTable."""

        model = Dashboard
        fields = ("dashboard_slug", "dashboard_uid", "actions")


class PanelViewTable(BaseTable):
    """Table for rendering panels for dashboards in the grafana plugin."""

    actions = TemplateColumn(
        template_code=_action_template("panels"),
        attrs={"td": {"class": "text-right noprint"}},
        verbose_name="",
    )

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta for class PanelViewTable."""

        model = Panel
        fields = ("command_name", "friendly_name", "panel_id", "dashboard", "actions")


class PanelVariableViewTable(BaseTable):
    """Table for rendering panels for dashboards in the grafana plugin."""

    actions = TemplateColumn(
        template_code=_action_template("variables"),
        attrs={"td": {"class": "text-right noprint"}},
        verbose_name="",
    )

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta for class PanelVariableViewTable."""

        model = PanelVariable
        fields = tuple(PanelVariable.csv_headers + ["actions"])
