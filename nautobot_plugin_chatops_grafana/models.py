"""Models for Grafana Plugin."""
from django.db import models
from django.shortcuts import reverse
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

    csv_headers = ["dashboard_slug", "dashboard_uid", "friendly_name"]

    class Meta:
        """Metadata for the model."""

        ordering = ["dashboard_slug"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.dashboard_slug}"

    def get_absolute_url(self):
        """Returns the Detail view for DeviceLifeCycleEoX models."""
        return reverse("plugins:nautobot_plugin_chatops_grafana:dashboards", kwargs={"pk": self.pk})

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
    active = models.BooleanField(default=False)

    csv_headers = ["dashboard", "command_name", "friendly_name", "panel_id", "active"]

    class Meta:
        """Metadata for the model."""

        ordering = ["command_name", "dashboard"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.command_name}"

    def to_csv(self):
        """Return fields for bulk view."""
        return self.dashboard, self.command_name, self.friendly_name, self.panel_id, self.active


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
    friendly_name = models.CharField(max_length=64)
    query = models.CharField(max_length=64)
    includeincmd = models.BooleanField(default=False)
    includeinurl = models.BooleanField(default=True)
    modelattr = models.CharField(max_length=64)
    value = models.TextField(max_length=64)
    response = models.CharField(max_length=255)
    filter = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)
    positional_order = models.IntegerField(default=100)

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
        "positional_order",
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
            self.positional_order,
        )
