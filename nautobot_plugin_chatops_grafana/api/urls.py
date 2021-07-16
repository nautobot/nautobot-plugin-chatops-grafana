"""Django urlpatterns declaration for nautobot_plugin_chatops_grafana plugin."""

# from django.urls import path

from nautobot.core.api import OrderedDefaultRouter
from nautobot_plugin_chatops_grafana.api.views.generic import NautobotPluginChatopsGrafanaRootView


urlpatterns = []

router = OrderedDefaultRouter()
router.APIRootView = NautobotPluginChatopsGrafanaRootView

app_name = "nautobot_plugin_chatops_grafana-api"

urlpatterns += router.urls
