"""Django urlpatterns declaration for nautobot_plugin_chatops_grafana plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_plugin_chatops_grafana.models import Dashboard, PanelVariable, Panel
from nautobot_plugin_chatops_grafana.views import (
    Dashboards,
    DashboardsCreate,
    DashboardsDelete,
    DashboardsEdit,
    DashboardsSync,
    DashboardsBulkImportView,
    DashboardsBulkDeleteView,
    DashboardBulkEditView,
    Panels,
    PanelsCreate,
    PanelsEdit,
    PanelsSync,
    PanelsDelete,
    PanelsBulkImportView,
    PanelsBulkDeleteView,
    PanelsBulkEditView,
    Variables,
    VariablesCreate,
    VariablesSync,
    VariablesEdit,
    VariablesDelete,
    VariablesBulkImportView,
    VariablesBulkDeleteView,
    VariablesBulkEditView,
)

urlpatterns = [
    # Dashboard specific views.
    path("dashboards/", Dashboards.as_view(), name="dashboards"),
    path(
        "dashboards/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="dashboard_changelog",
        kwargs={"model": Dashboard},
    ),
    path("dashboards/add/", DashboardsCreate.as_view(), name="dashboard_add"),
    path("dashboards/sync/", DashboardsSync.as_view(), name="dashboard_sync"),
    path("dashboards/<uuid:pk>/edit/", DashboardsEdit.as_view(), name="dashboard_edit"),
    path("dashboards/edit/", DashboardBulkEditView.as_view(), name="dashboard_bulk_edit"),
    path("dashboards/<uuid:pk>/delete/", DashboardsDelete.as_view(), name="dashboard_delete"),
    path("dashboards/delete/", DashboardsBulkDeleteView.as_view(), name="dashboard_bulk_delete"),
    path("dashboards/import/", DashboardsBulkImportView.as_view(), name="dashboard_import"),
    # Panel specific views.
    path("panels/", Panels.as_view(), name="panel"),
    path(
        "panels/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="panel_changelog",
        kwargs={"model": Panel},
    ),
    path("panels/add/", PanelsCreate.as_view(), name="panel_add"),
    path("panels/sync/", PanelsSync.as_view(), name="panel_sync"),
    path("panels/<uuid:pk>/edit/", PanelsEdit.as_view(), name="panel_edit"),
    path("panels/edit/", PanelsBulkEditView.as_view(), name="panel_bulk_edit"),
    path("panels/<uuid:pk>/delete/", PanelsDelete.as_view(), name="panel_delete"),
    path("panels/delete/", PanelsBulkDeleteView.as_view(), name="panel_bulk_delete"),
    path("panels/import/", PanelsBulkImportView.as_view(), name="panel_import"),
    # Panel-variables specific views.
    path("variables/", Variables.as_view(), name="panelvariables"),
    path(
        "variables/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="panelvariable_changelog",
        kwargs={"model": PanelVariable},
    ),
    path("variables/add/", VariablesCreate.as_view(), name="panelvariable_add"),
    path("variables/sync/", VariablesSync.as_view(), name="panelvariable_sync"),
    path("variables/<uuid:pk>/edit/", VariablesEdit.as_view(), name="panelvariable_edit"),
    path("variables/edit/", VariablesBulkEditView.as_view(), name="panelvariable_bulk_edit"),
    path("variables/<uuid:pk>/delete/", VariablesDelete.as_view(), name="panelvariable_delete"),
    path("variables/delete/", VariablesBulkDeleteView.as_view(), name="panelvariable_bulk_delete"),
    path("variables/import/", VariablesBulkImportView.as_view(), name="panelvariable_import"),
]
