"""Models for Grafana Plugin."""
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from nautobot.extras.utils import extras_features
from nautobot.core.models.generics import PrimaryModel, OrganizationalModel


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "statuses",
    "webhooks",
)
class Dashboard(PrimaryModel):
    """Model for dashboards."""

    dashboard_slug = models.CharField(max_length=255, unique=True, blank=False)
    friendly_name = models.CharField(max_length=255, default="", blank=True)
    dashboard_uid = models.CharField(max_length=64, unique=True, blank=False)

    csv_headers = ["slug", "uid", "friendly_name"]

    class Meta:
        """Metadata for the model."""

        ordering = ["dashboard_slug"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.dashboard_slug}"

    def to_csv(self):
        """Return fields for bulk view."""
        return self.dashboard_slug, self.dashboard_uid, self.friendly_name


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class Panel(OrganizationalModel):
    """Model for Dashboard Panels."""

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    command_name = models.CharField(max_length=64, blank=False)
    friendly_name = models.CharField(max_length=64, default="", blank=False)
    panel_id = models.IntegerField(blank=False)

    csv_headers = ["dashboard", "command_name", "friendly_name", "panel_id"]

    class Meta:
        """Metadata for the model."""

        ordering = ["command_name", "dashboard"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.command_name}"

    def to_csv(self):
        """Return fields for bulk view."""
        return self.dashboard, self.command_name, self.friendly_name, self.panel_id


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class PanelVariable(OrganizationalModel):
    """Model for Dashboard Panel Variables."""

    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, blank=False)
    friendly_name = models.CharField(max_length=64, default="")
    query = models.CharField(max_length=64, default="")
    includeincmd = models.BooleanField(default=False)
    includeinurl = models.BooleanField(default=True)
    modelattr = models.CharField(max_length=64, default="")
    value = models.CharField(max_length=64, default="")
    response = models.CharField(max_length=255)
    filter = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    csv_headers = [
        "panel",
        "name",
        "friendly_name",
        "query",
        "includeincmd",
        "includeinurl",
        "modelattr",
        "value",
        "response",
        "filter",
    ]

    class Meta:
        """Metadata for the model."""

        ordering = ["name"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.name}"

    def to_csv(self):
        """Return fields for bulk view."""
        return (
            self.panel,
            self.name,
            self.friendly_name,
            self.query,
            self.includeincmd,
            self.includeinurl,
            self.modelattr,
            self.value,
            self.response,
            self.filter,
        )
