"""Navigation for Circuit Maintenance."""
from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton, ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_plugin_chatops_grafana:dashboards",
        permissions=["nautobot_plugin_chatops_grafana.dashboards_read"],
        link_text="Dashboards",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_chatops_grafana:dashboards_create",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_chatops_grafana.dashboards_create"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_plugin_chatops_grafana:panels",
        permissions=["nautobot_plugin_chatops_grafana.panels_read"],
        link_text="Panels",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_chatops_grafana:panels_create",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_chatops_grafana.panels_create"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_plugin_chatops_grafana:variables",
        permissions=["nautobot_plugin_chatops_grafana.variables_read"],
        link_text="Variables",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_chatops_grafana:variables_create",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_chatops_grafana.variables_create"],
            ),
        ),
    ),
)
