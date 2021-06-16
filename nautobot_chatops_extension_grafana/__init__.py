"""Plugin declaration for nautobot_chatops_extension_grafana."""

__version__ = "0.1.0"

from nautobot.extras.plugins import PluginConfig


class NautobotChatopsExtensionGrafanaConfig(PluginConfig):
    """Plugin configuration for the nautobot_chatops_extension_grafana plugin."""

    name = "nautobot_chatops_extension_grafana"
    verbose_name = "Nautobot Chatops Extension Grafana"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot Chatops Extension Grafana."
    base_url = "nautobot-chatops-extension-grafana"
    required_settings = []
    min_version = "1.0.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}


config = NautobotChatopsExtensionGrafanaConfig  # pylint:disable=invalid-name
