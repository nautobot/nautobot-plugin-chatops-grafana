"""Navigation for Circuit Maintenance."""
from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton, ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_plugin_chatops_grafana:dashboards",
        permissions=["nautobot_plugin_chatops_grafana.dashboards_read"],
        link_text="Dashboards",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_chatops_grafana:dashboard_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_chatops_grafana.dashboard_add"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_plugin_chatops_grafana:panel",
        permissions=["nautobot_plugin_chatops_grafana.panel_read"],
        link_text="Panels",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_chatops_grafana:panel_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_chatops_grafana.panel_add"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_plugin_chatops_grafana:panelvariables",
        permissions=["nautobot_plugin_chatops_grafana.panelvariables_read"],
        link_text="Variables",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_chatops_grafana:panelvariable_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_chatops_grafana.panelvariable_add"],
            ),
        ),
    ),
)
