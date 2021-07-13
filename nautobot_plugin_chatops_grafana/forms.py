"""Forms for Nautobot."""

from django.forms import ModelForm, CharField, IntegerField, BooleanField, JSONField, ModelChoiceField
from nautobot.utilities.forms import BootstrapMixin
from nautobot_plugin_chatops_grafana.models import Dashboard, Panel, PanelVariable


class DashboardsForm(BootstrapMixin, ModelForm):
    """Form for editing Dashboard instances."""

    dashboard_slug = CharField(max_length=64)
    dashboard_uid = CharField(max_length=64)
    friendly_name = CharField(max_length=255)

    class Meta:
        """Metaclass attributes of Dashboard."""

        model = Dashboard

        fields = ("dashboard_slug", "dashboard_uid", "friendly_name")


class PanelsForm(BootstrapMixin, ModelForm):
    """Form for editing Panel instances."""

    dashboard = ModelChoiceField(queryset=Dashboard.objects.all())
    command_name = CharField(max_length=64)
    friendly_name = CharField(max_length=64)
    panel_id = IntegerField()

    class Meta:
        """Metaclass attributes of Panel."""

        model = Panel

        fields = ("dashboard", "command_name", "friendly_name", "panel_id")


class PanelVariablesForm(BootstrapMixin, ModelForm):
    """Form for editing Panel Variable instances."""

    panel = ModelChoiceField(queryset=Panel.objects.all())
    name = CharField(max_length=32)
    friendly_name = CharField(max_length=64, required=False)
    query = CharField(max_length=64, required=False)
    includeincmd = BooleanField()
    includeinurl = BooleanField()
    modelattr = CharField(max_length=64, required=False)
    value = CharField(max_length=64, required=False)
    response = CharField(max_length=255, required=False)
    filter = JSONField(required=False)

    class Meta:
        """Metaclass attributes of Panel Variable."""

        model = PanelVariable

        fields = tuple(PanelVariable.csv_headers)
