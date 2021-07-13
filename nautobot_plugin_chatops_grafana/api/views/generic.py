"""API Views for Nautobot Plugin Chatops Grafana."""
from rest_framework.routers import APIRootView


class NautobotPluginChatopsGrafanaRootView(APIRootView):
    """Nautobot Chatops API root view."""

    def get_view_name(self):
        """Return name for the Nautobot Plugin Chatops Grafana API Root."""
        return "Nautobot Plugin Chatops Grafana"
