[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

**This component will set up the following platforms.**

| Platform | Description         |
| -------- | ------------------- |
| `sensor` | Show info from API. |

**Currently available Sensors**

| Sensor                             | Description                                      |
| ---------------------------------- | ------------------------------------------------ |
| `sensor.ssn`                       | Current Sunspot Number.                          |
| `sensor.solar_flux_index`          | Current Solar Flux Index.                        |
| `sensor.planetary_k_index`         | Current Planetary K-Index.                       |
| `sensor.a_index`                   | Current A-Index.                                 |
| `sensor.a_index_2_day`             | 2-Day A-Index.                                   |
| `sensor.a_index_3_day`             | 3-Day A-Index.                                   |
| `sensor.polar_cap_absorption`      | A color-scale indication of polar cap absorption |
| `sensor.x_class_1_day_probability` | Probability of an X-Class flare within one day.  |
| `sensor.m_class_1_day_probability` | Probability of an M-Class flare within one day.  |

![example][exampleimg]

{% if not installed %}

## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "NOAA Space Weather".

{% endif %}

## Configuration is done in the UI

<!---->

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[buymecoffee]: https://www.buymeacoffee.com/tcarwash
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/tcarwash/home-assistant_noaa-space-weather.svg?style=for-the-badge
[commits]: https://github.com/tcarwash/home-assistant_noaa-space-weather/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/tcarwash/home-assistant_noaa-space-weather/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/tcarwash/home-assistant_noaa-space-weather.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40tcarwash-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/tcarwash/home-assistant_noaa-space-weather.svg?style=for-the-badge
[releases]: https://github.com/tcarwash/home-assistant_noaa-space-weather/releases
[user_profile]: https://github.com/tcarwash
