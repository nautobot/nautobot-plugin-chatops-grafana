"""Views module for the nautobot_plugin_chatops_grafana plugin.

The views implemented in this module act as endpoints for various chat platforms
to send requests and notifications to.
"""

from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from nautobot.core.views.generic import (
    ObjectEditView,
    ObjectDeleteView,
    ObjectListView,
    BulkImportView,
    BulkDeleteView,
    BulkEditView,
)
from nautobot.utilities.forms import ConfirmationForm
from nautobot_plugin_chatops_grafana.diffsync.sync import run_dashboard_sync, run_panels_sync
from nautobot_plugin_chatops_grafana.tables import PanelViewTable, DashboardViewTable, PanelVariableViewTable
from nautobot_plugin_chatops_grafana.models import Panel, Dashboard, PanelVariable
from nautobot_plugin_chatops_grafana.grafana import handler
from nautobot_plugin_chatops_grafana.filters import DashboardFilter, PanelFilter, VariablFilter
from nautobot_plugin_chatops_grafana.forms import (
    DashboardsForm,
    DashboardsFilterForm,
    DashboardCSVForm,
    DashboardBulkEditForm,
    PanelsForm,
    PanelsSyncForm,
    PanelsCSVForm,
    PanelsFilterForm,
    PanelsBulkEditForm,
    PanelVariablesForm,
    PanelVariablesFilterForm,
    PanelVariablesBulkEditForm,
    PanelVariablesCSVForm,
)

# -------------------------------------------------------------------------------------
# Dashboard Specific Views
# -------------------------------------------------------------------------------------


class Dashboards(ObjectListView):
    """View for showing dashboard configuration."""

    queryset = Dashboard.objects.all()
    filterset = DashboardFilter
    filterset_form = DashboardsFilterForm
    table = DashboardViewTable
    action_buttons = ("add", "import")
    template_name = "nautobot_plugin_chatops_grafana/dashboard_list.html"

    def get_required_permission(self):
        """Return required view permission."""
        return "nautobot_plugin_chatops_grafana.dashboard_read"


class DashboardsCreate(PermissionRequiredMixin, ObjectEditView):
    """View for creating a new Dashboard."""

    permission_required = "nautobot_plugin_chatops_grafana.dashboard_add"
    model = Dashboard
    queryset = Dashboard.objects.all()
    model_form = DashboardsForm
    template_name = "nautobot_plugin_chatops_grafana/dashboards_edit.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"


class DashboardsEdit(DashboardsCreate):
    """View for editing an existing Dashboard."""

    permission_required = "nautobot_plugin_chatops_grafana.dashboard_edit"


class DashboardsSync(PermissionRequiredMixin, ObjectDeleteView):
    """View for syncing Grafana Dashboards with the Grafana API."""

    permission_required = "nautobot_plugin_chatops_grafana.dashboard_sync"
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
    permission_required = "nautobot_plugin_chatops_grafana.dashboard_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"


class DashboardsBulkImportView(BulkImportView):
    """View for bulk import of eox notices."""

    queryset = Dashboard.objects.all()
    model_form = DashboardCSVForm
    table = DashboardViewTable
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"


class DashboardsBulkDeleteView(BulkDeleteView):
    """View for deleting one or more Dashboard records."""

    queryset = Dashboard.objects.all()
    table = DashboardViewTable
    bulk_delete_url = "plugins:nautobot_plugin_chatops_grafana:dashboard_bulk_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:dashboards"

    def get_required_permission(self):
        """Return required delete permission."""
        return "nautobot_plugin_chatops_grafana.dashboard_delete"


class DashboardBulkEditView(BulkEditView):
    """View for editing one or more Dashboard records."""

    queryset = Dashboard.objects.all()
    filterset = DashboardFilter
    table = DashboardViewTable
    form = DashboardBulkEditForm
    bulk_edit_url = "plugins:nautobot_plugin_chatops_grafana:dashboard_bulk_edit"

    def get_required_permission(self):
        """Return required change permission."""
        return "nautobot_plugin_chatops_grafana.dashboard_edit"


# -------------------------------------------------------------------------------------
# Panel Specific Views
# -------------------------------------------------------------------------------------


class Panels(ObjectListView):
    """View for showing panels configuration."""

    queryset = Panel.objects.all()
    filterset = PanelFilter
    filterset_form = PanelsFilterForm
    table = PanelViewTable
    action_buttons = ("add", "import")
    template_name = "nautobot_plugin_chatops_grafana/panel_list.html"

    def get_required_permission(self):
        """Return required view permission."""
        return "nautobot_plugin_chatops_grafana.panel_read"


class PanelsCreate(PermissionRequiredMixin, ObjectEditView):
    """View for creating a new Panel."""

    permission_required = "nautobot_plugin_chatops_grafana.panel_add"
    model = Panel
    queryset = Panel.objects.all()
    model_form = PanelsForm
    template_name = "nautobot_plugin_chatops_grafana/panels_edit.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panel"


class PanelsEdit(PanelsCreate):
    """View for editing an existing Panel."""

    permission_required = "nautobot_plugin_chatops_grafana.panel_edit"


class PanelsSync(PermissionRequiredMixin, ObjectEditView):
    """View for synchronizing data between the Grafana Dashboard Panels and Nautobot."""

    permission_required = "nautobot_plugin_chatops_grafana.panel_sync"
    model = Panel
    queryset = Panel.objects.all()
    model_form = PanelsSyncForm
    template_name = "nautobot_plugin_chatops_grafana/panels_sync.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panel"

    def get_permission_required(self):
        """Permissions over-rride for the Panels Sync view."""
        return "nautobot_plugin_chatops_grafana.panel_sync"

    def post(self, request, *args, **kwargs):
        """Post request for the Panels Sync view."""
        dashboard_pk = request.POST.get("dashboard")
        if not dashboard_pk:
            messages.error(request, "Unable to determine Grafana Dashboard!")
            return redirect(reverse("plugins:nautobot_plugin_chatops_grafana:panel"))

        dashboard = Dashboard.objects.get(pk=dashboard_pk)

        sync_data = run_panels_sync(dashboard, request.POST.get("delete") == "true")
        if not sync_data:
            messages.info(request, "No diffs found for the Grafana Dashboards!")
        else:
            messages.success(request, "Grafana Dashboards synchronization complete!")

        return redirect(reverse("plugins:nautobot_plugin_chatops_grafana:panel"))


class PanelsDelete(PermissionRequiredMixin, ObjectDeleteView):
    """View for deleting one or more Panel records."""

    queryset = Panel.objects.all()
    permission_required = "nautobot_plugin_chatops_grafana.panel_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panel"


class PanelsBulkImportView(BulkImportView):
    """View for bulk import of Panels."""

    queryset = Panel.objects.all()
    model_form = PanelsCSVForm
    table = PanelViewTable
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panel"


class PanelsBulkDeleteView(BulkDeleteView):
    """View for deleting one or more Panels records."""

    queryset = Panel.objects.all()
    table = PanelViewTable
    bulk_delete_url = "plugins:nautobot_plugin_chatops_grafana:panel_bulk_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panel"

    def get_required_permission(self):
        """Return required delete permission."""
        return "nautobot_plugin_chatops_grafana.panel_delete"


class PanelsBulkEditView(BulkEditView):
    """View for editing one or more Panels records."""

    queryset = Panel.objects.all()
    filterset = PanelsFilterForm
    table = PanelViewTable
    form = PanelsBulkEditForm
    bulk_edit_url = "plugins:nautobot_plugin_chatops_grafana:panel_bulk_edit"

    def get_required_permission(self):
        """Return required change permission."""
        return "nautobot_plugin_chatops_grafana.panel_edit"


# -------------------------------------------------------------------------------------
# Panel Variable Specific Views
# -------------------------------------------------------------------------------------


class Variables(ObjectListView):
    """View for showing panel-variables configuration."""

    queryset = PanelVariable.objects.all()
    filterset = VariablFilter
    filterset_form = PanelVariablesFilterForm
    table = PanelVariableViewTable
    action_buttons = ("add", "import")

    def get_required_permission(self):
        """Return required view permission."""
        return "nautobot_plugin_chatops_grafana.panelvariable_read"


class VariablesCreate(PermissionRequiredMixin, ObjectEditView):
    """View for creating a new Variable."""

    permission_required = "nautobot_plugin_chatops_grafana.panelvariable_add"
    model = PanelVariable
    queryset = PanelVariable.objects.all()
    model_form = PanelVariablesForm
    template_name = "nautobot_plugin_chatops_grafana/variables_edit.html"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panelvariables"


class VariablesEdit(VariablesCreate):
    """View for editing an existing Variable."""

    permission_required = "nautobot_plugin_chatops_grafana.panelvariable_edit"


class VariablesDelete(PermissionRequiredMixin, ObjectDeleteView):
    """View for deleting one or more Variable records."""

    queryset = PanelVariable.objects.all()
    permission_required = "nautobot_plugin_chatops_grafana.panelvariable_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panelvariables"


class VariablesBulkImportView(BulkImportView):
    """View for bulk import of Variables."""

    queryset = PanelVariable.objects.all()
    model_form = PanelVariablesCSVForm
    table = PanelVariableViewTable
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panelvariables"


class VariablesBulkDeleteView(BulkDeleteView):
    """View for deleting one or more Variable records."""

    queryset = PanelVariable.objects.all()
    table = PanelVariableViewTable
    bulk_delete_url = "plugins:nautobot_plugin_chatops_grafana:panelvariable_bulk_delete"
    default_return_url = "plugins:nautobot_plugin_chatops_grafana:panelvariables"

    def get_required_permission(self):
        """Return required delete permission."""
        return "nautobot_plugin_chatops_grafana.panelvariable_delete"


class VariablesBulkEditView(BulkEditView):
    """View for editing one or more Variable records."""

    queryset = PanelVariable.objects.all()
    filterset = PanelVariablesFilterForm
    table = PanelVariableViewTable
    form = PanelVariablesBulkEditForm
    bulk_edit_url = "plugins:nautobot_plugin_chatops_grafana:panelvariable_bulk_edit"

    def get_required_permission(self):
        """Return required change permission."""
        return "nautobot_plugin_chatops_grafana.panelvariable_edit"
