"""Django urlpatterns declaration for nautobot_plugin_chatops_grafana plugin."""

from django.urls import path

from nautobot.core.api import OrderedDefaultRouter
from nautobot_plugin_chatops_grafana.api.views.generic import NautobotPluginChatopsGrafanaRootView
from nautobot_plugin_chatops_grafana.api.views.grafana import GrafanaDashboards


urlpatterns = [path("dashboards/", GrafanaDashboards.as_view(), name="grafana_dashboards")]

router = OrderedDefaultRouter()
router.APIRootView = NautobotPluginChatopsGrafanaRootView

app_name = "nautobot_plugin_chatops_grafana-api"

urlpatterns += router.urls
