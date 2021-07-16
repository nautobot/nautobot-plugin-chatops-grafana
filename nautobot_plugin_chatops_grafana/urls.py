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
    Panels,
    PanelsCreate,
    PanelsEdit,
    PanelsSync,
    PanelsDelete,
    Variables,
    VariablesCreate,
    VariablesEdit,
    VariablesDelete,
)

urlpatterns = [
    # Dashboard specific views.
    path("dashboards/", Dashboards.as_view(), name="dashboards"),
    path(
        "dashboards/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="dashboards_changelog",
        kwargs={"model": Dashboard},
    ),
    path("dashboards/add/", DashboardsCreate.as_view(), name="dashboards_create"),
    path("dashboards/sync/", DashboardsSync.as_view(), name="dashboards_sync"),
    path("dashboards/<uuid:pk>/edit/", DashboardsEdit.as_view(), name="dashboards_update"),
    path("dashboards/<uuid:pk>/delete/", DashboardsDelete.as_view(), name="dashboards_delete"),
    # Panel specific views.
    path("panels/", Panels.as_view(), name="panels"),
    path(
        "panels/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="panels_changelog",
        kwargs={"model": Panel},
    ),
    path("panels/add/", PanelsCreate.as_view(), name="panels_create"),
    path("panels/sync/", PanelsSync.as_view(), name="panels_sync"),
    path("panels/<uuid:pk>/edit/", PanelsEdit.as_view(), name="panels_update"),
    path("panels/<uuid:pk>/delete/", PanelsDelete.as_view(), name="panels_delete"),
    # Panel-variables specific views.
    path("variables/", Variables.as_view(), name="variables"),
    path(
        "variables/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="variables_changelog",
        kwargs={"model": PanelVariable},
    ),
    path("variables/add/", VariablesCreate.as_view(), name="variables_create"),
    path("variables/<uuid:pk>/edit/", VariablesEdit.as_view(), name="variables_update"),
    path("variables/<uuid:pk>/delete/", VariablesDelete.as_view(), name="variables_delete"),
]
