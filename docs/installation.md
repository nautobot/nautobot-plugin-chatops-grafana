# Installation Guide
A set of instructions that will help you get started with the Nautobot Grafana Plugin. This document is intended to
serve as a guide for the requirements and installation on the plugin within a Nautobot environment.

## Requirements
Prior to installing the Nautobot Grafana Plugin, you will need to have a minimum of the following installed:
 * [Nautobot](https://nautobot.readthedocs.io/en/stable/installation/nautobot/) installed and configured.
 * [Grafana](https://grafana.com/docs/grafana/latest/installation/) application installed and configured with dashboards and panels.
 * [Grafana Image Rendering Service](https://grafana.com/docs/grafana/latest/administration/image_rendering/) installed.
 * [Grafana Image Rending Plugin for Grafana](https://grafana.com/grafana/plugins/grafana-image-renderer/) installed in your Grafana application.
 * [Nautobot Plugin ChatOps](https://github.com/nautobot/nautobot-plugin-chatops/blob/develop/docs/chat_setup/chat_setup.md) installed and configured for your specific chat platform.

## Plug-In Installation
The plugin is available as a Python package in pypi and can be installed with pip

```shell
pip install nautobot-plugin-chatops-grafana
```

> This plugin is compatible with Nautobot 1.0.0 and higher

To ensure Nautobot Chatops Extension Grafana is automatically re-installed during future upgrades, create a file named 
`local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and 
list the `nautobot-plugin-chatops-grafana` package:

```no-highlight
# echo nautobot-plugin-chatops-grafana >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `nautobot_configuration.py`

## Nautobot Server Configuration
As the nautobot user, you will now edit the `nautobot_config.py` file.

There are also some platform-specific requirements to configure.
Some values from your chat platform-specific configuration in the prior section are configured in nautobot_config.py.

```python
# In your configuration.py
PLUGINS = ["nautobot_plugin_chatops_grafana"]

# PLUGINS_CONFIG = {
#     "nautobot_plugin_chatops_grafana": {
#         "grafana_url": os.environ.get("GRAFANA_URL", ""),
#         "grafana_api_key": os.environ.get("GRAFANA_API_KEY", ""),
#         "default_width": 0,
#         "default_height": 0,
#         "default_theme": "dark",
#         "default_timespan": "0",
#         "grafana_org_id": 1,
#         "default_tz": "America/Denver",
#     },
# }
```

The plugin behavior can be controlled with the following list of settings

 * `grafana_url`:  (REQUIRED)
    * This will be the base url that the Grafana application is hosted at.
 * `grafana_api_key`: (REQUIRED)
    * API key generated with Grafana, found in `<grafana_base_url>/org/apikeys`.
    * NOTE: The Grafana API key only needs to have `Viewer` permissions assigned!
 * `default_width`: (Default `0`)
    * Grafana image width when rendered into the chat client. Default will render width dynamically.
 * `default_height`: (Default `0`)
    * Grafana image height when rendered into the chat client. Default will render height dynamically.
 * `default_theme`: (Default `dark`)
    * Theme color to use when generating rendered Grafana images. Options are [`dark`, `light`]
 * `default_timespan`: (Default `0`)
    * Timespan that data is collected on a panel in Grafana. Default action is to use the defined timespan in Grafana.
 * `grafana_org_id`: (Default `1`)
    * Grafana organization Id to associate with this plugin. Found in `<grafana_base_url>//admin/orgs`.
 * `default_tz`: (Default `America/Denver`)
    * Timezone in which the renderer will render charts and graphs in. 
 
> As a sudo-enabled user, restart the nautobot and nautobot-worker process after updating nautobot_config.py.


## Chat Client Configuration
As noted in the requirements section of this document, you will need to have the nautobot-plugin-chatops plugin installed
prior to installing this plugin as it leverages the chatops abstract methods to communicate with your chat client.

To enable the `/grafana` chat command on your chat client, you may need to define a slash command within your chat configuration.
See the item `3.` on the [Slack Chat Setup](https://github.com/nautobot/nautobot-plugin-chatops/blob/develop/docs/chat_setup/slack_setup.md)
instructions in the nautobot-plugin-chatops documentation.