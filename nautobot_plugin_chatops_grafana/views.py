"""Views module for the nautobot_plugin_chatops_grafana plugin.

The views implemented in this module act as endpoints for various chat platforms
to send requests and notifications to.
"""

from django.views import View
from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from nautobot.core.views.generic import ObjectEditView, ObjectDeleteView
from nautobot.utilities.forms import ConfirmationForm
from nautobot_plugin_chatops_grafana.diffsync.sync import run_dashboard_sync, run_panels_sync
from nautobot_plugin_chatops_grafana.tables import PanelViewTable, DashboardViewTable, PanelVariableViewTable
from nautobot_plugin_chatops_grafana.models import Panel, Dashboard, PanelVariable
from nautobot_plugin_chatops_grafana.grafana import handler
from nautobot_plugin_chatops_grafana.forms import DashboardsForm, PanelsForm, PanelsSyncForm, PanelVariablesForm


class Dashboards(View):
    """View for showing dashboard configuration."""

    http_method_names = ["get"]
    table = DashboardViewTable
    permission_required = "nautobot_plugin_chatops_grafana.dashboards_read"

    def get(self, request, *args, **kwargs):
        """Get request for the Dashboard view."""
        table = self.table(data=Dashboard.objects.all(), user=request.user)

        return render(
            request,
            "nautobot_plugin_chatops_grafana/dashboards.html",
            {"table": table},
        )


class DashboardsCreate(PermissionRequiredMixin, ObjectEditView):
    """View for creating a new Dashboard."""

    permission_required = "nautobot_plugin_chatops_grafana.dashboards_create"
    model = Dashboard
    queryset = Dashboard.objects.all()
    model_form = DashboardsForm
    template_name = "nautobot_plugin_chatops_grafana/dashboards_edit.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"


class DashboardsEdit(DashboardsCreate):
    """View for editing an existing Dashboard."""

    permission_required = "nautobot_plugin_chatops_grafana.dashboards_update"


class DashboardsSync(PermissionRequiredMixin, ObjectDeleteView):
    """View for syncing Grafana Dashboards with the Grafana API."""

    permission_required = "nautobot_plugin_chatops_grafana.dashboards_sync"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"

    def get(self, request, **kwargs):
        """Get request for the Dashboard Sync view."""
        return render(
            request,
            "nautobot_plugin_chatops_grafana/sync_confirmation.html",
            {
                "form": ConfirmationForm(initial=request.GET),
                "grafana_url": handler.config.grafana_url,
                "return_url": reverse("plugins:nautobot_plugin_chatops_grafana:dashboards"),
            },
        )

    def post(self, request, **kwargs):
        """Post request for the Dashboard Sync view."""
        form = ConfirmationForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Form validation failed.")

        else:
            sync_data = run_dashboard_sync(request.POST.get("delete") == "true")
            if not sync_data:
                messages.info(request, "No diffs found for the Grafana Dashboards!")
            else:
                messages.success(request, "Grafana Dashboards synchronization complete!")

        return redirect(reverse("plugins:nautobot_plugin_chatops_grafana:dashboards"))


class DashboardsDelete(PermissionRequiredMixin, ObjectDeleteView):
    """View for deleting one or more Dashboard records."""

    queryset = Dashboard.objects.all()
    permission_required = "nautobot_plugin_chatops_grafana.dashboards_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"


class Panels(View):
    """View for showing panels configuration."""

    http_method_names = ["get"]
    table = PanelViewTable

    def get(self, request, *args, **kwargs):
        """Get request for the Panels view."""
        table = self.table(Panel.objects.all(), user=request.user)

        return render(
            request,
            "nautobot_plugin_chatops_grafana/panels.html",
            {"table": table},
        )


class PanelsCreate(PermissionRequiredMixin, ObjectEditView):
    """View for creating a new Panel."""

    permission_required = "nautobot_plugin_chatops_grafana.panels_create"
    model = Panel
    queryset = Panel.objects.all()
    model_form = PanelsForm
    template_name = "nautobot_plugin_chatops_grafana/panels_edit.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panels"


class PanelsEdit(PanelsCreate):
    """View for editing an existing Panel."""

    permission_required = "nautobot_plugin_chatops_grafana.panels_update"


class PanelsSync(PermissionRequiredMixin, ObjectEditView):
    """View for synchronizing data between the Grafana Dashboard Panels and Nautobot."""

    permission_required = "nautobot_plugin_chatops_grafana.panels_sync"
    model = Panel
    queryset = Panel.objects.all()
    model_form = PanelsSyncForm
    template_name = "nautobot_plugin_chatops_grafana/panels_sync.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panels"

    def get_permission_required(self):
        """Permissions over-rride for the Panels Sync view."""
        return "nautobot_plugin_chatops_grafana.panels_sync"

    def post(self, request, *args, **kwargs):
        """Post request for the Panels Sync view."""
        dashboard_pk = request.POST.get("dashboard")
        if not dashboard_pk:
            messages.error(request, "Unable to determine Grafana Dashboard!")
            return redirect(reverse("plugins:nautobot_plugin_chatops_grafana:panels"))

        dashboard = Dashboard.objects.get(pk=dashboard_pk)

        sync_data = run_panels_sync(dashboard, request.POST.get("delete") == "true")
        if not sync_data:
            messages.info(request, "No diffs found for the Grafana Dashboards!")
        else:
            messages.success(request, "Grafana Dashboards synchronization complete!")

        return redirect(reverse("plugins:nautobot_plugin_chatops_grafana:panels"))


class PanelsDelete(PermissionRequiredMixin, ObjectDeleteView):
    """View for deleting one or more Panel records."""

    queryset = Panel.objects.all()
    permission_required = "nautobot_plugin_chatops_grafana.panels_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panels"


class Variables(View):
    """View for showing panel-variables configuration."""

    http_method_names = ["get"]
    table = PanelVariableViewTable

    def get(self, request, *args, **kwargs):
        """Get request for the Variables view."""
        table = self.table(PanelVariable.objects.all(), user=request.user)

        return render(
            request,
            "nautobot_plugin_chatops_grafana/variables.html",
            {"table": table},
        )


class VariablesCreate(PermissionRequiredMixin, ObjectEditView):
    """View for creating a new Variable."""

    permission_required = "nautobot_plugin_chatops_grafana.variables_create"
    model = PanelVariable
    queryset = PanelVariable.objects.all()
    model_form = PanelVariablesForm
    template_name = "nautobot_plugin_chatops_grafana/variables_edit.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:variables"


class VariablesEdit(VariablesCreate):
    """View for editing an existing Variable."""

    permission_required = "nautobot_plugin_chatops_grafana.variables_update"


class VariablesDelete(PermissionRequiredMixin, ObjectDeleteView):
    """View for deleting one or more Variable records."""

    queryset = PanelVariable.objects.all()
    permission_required = "nautobot_plugin_chatops_grafana.variables_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:variables"
