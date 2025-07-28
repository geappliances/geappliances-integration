# GE Appliances Integration

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![Community Forum][forum-shield]][forum]

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GE+Appliances&category=Integration&repository=https%3A%2F%2Fgithub.com%2Fgeappliances%2Fhacs-integration)

_Integration to integrate with [GE Appliances](https://www.geappliances.com/)._

This integration will automatically use the [Appliance API](https://github.com/geappliances/public-appliance-api-documentation) to find public ERDs on an appliance and set up corresponding entities in Home Assistant. It is designed to be a "batteries-included" option for users who want to quickly and easily get their appliances talking to Home Assistant. Users wanting a more customized experience might be interested in [using YAML with the MQTT integration](https://github.com/geappliances/home-assistant-examples) to communicate with their appliances.

## Installation

1. The preferred method of installing this integration is through the [Home Assistant Community Store][hacs].

<!---->

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `geappliances`.
1. Download _all_ the files from the `custom_components/geappliances/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "GE Appliances"


## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/geappliances/hacs-integration.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/geappliances/hacs-integration.svg?style=for-the-badge
[releases]: https://github.com/geappliances/hacs-integration/releases
[hacs]: https://www.hacs.xyz
