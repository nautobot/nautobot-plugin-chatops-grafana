"""Plugin declaration for nautobot_plugin_chatops_grafana."""

__version__ = "1.0.1"

from nautobot.extras.plugins import PluginConfig


class NautobotPluginChatopsGrafanaConfig(PluginConfig):
    """Plugin configuration for the nautobot_plugin_chatops_grafana plugin."""

    name = "nautobot_plugin_chatops_grafana"
    verbose_name = "Nautobot Plugin Chatops Grafana"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot Plugin Chatops Grafana."
    base_url = "nautobot-plugin-chatops-grafana"
    required_settings = []
    min_version = "1.0.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}


config = NautobotPluginChatopsGrafanaConfig  # pylint:disable=invalid-name
