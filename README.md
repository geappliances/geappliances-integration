# GE Appliances Integration

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![Community Forum][forum-shield]][forum]

_Integration to integrate with [GE Appliances][ge_appliances]._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from blueprint API.
`switch` | Switch something `True` or `False`.

## Installation

1. The preferred method of installing this integration is through the [Home Assistant Community Store][hacs]

<!---->

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `geappliances`.
1. Download _all_ the files from the `custom_components/geappliances/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "GE Appliances"

## Configuration is done in the UI

<!---->


## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[ge_appliances]: https://www.geappliances.com/
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/geappliances/applcommon.ge-appliances-integration.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/geappliances/applcommon.ge-appliances-integration.svg?style=for-the-badge
[releases]: https://github.com/geappliances/applcommon.ge-appliances-integration/releases
[hacs]: https://www.hacs.xyz
