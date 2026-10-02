# NOAA Space Weather

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

A (non-official) home assistant integration for the NOAA Space Weather Prediction Center API.

_Neither this integration nor it's developer have any affiliation with NOAA._

**This component will set up the following platforms.**

| Platform | Description                            |
| -------- | -------------------------------------- |
| `sensor` | Show info from NOAA Space Weather API. |

**These sensors are currently available**
| Sensor | Description |
| ----------------------------------------- | ---------------------------------------------- |
| `sensor.ssn` | Current Sunspot Number. |
| `sensor.solar_flux_index` | Current Solar Flux Index. |
| `sensor.planetary_k_index` | Current Planetary K-Index. |
| `sensor.a_index` | Predicted A-Index. |
| `sensor.a_index_2_day` | Predicted 2-Day A-Index. |
| `sensor.a_index_3_day` | Predicted 3-Day A-Index. |
| `sensor.polar_cap_absorption` | A color-scale indication of polar cap absorption |
| `sensor.x_class_1_day_probability` | Probability of an X-Class flare within one day.|
| `sensor.m_class_1_day_probability` | Probability of an M-Class flare within one day.|

![example][exampleimg]

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `noaa_space_weather`.
4. Download _all_ the files from the `custom_components/noaa_space_weather/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "NOAA Space Weather"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/noaa_space_weather/translations/en.json
custom_components/noaa_space_weather/translations/fr.json
custom_components/noaa_space_weather/translations/nb.json
custom_components/noaa_space_weather/translations/sv.json
custom_components/noaa_space_weather/__init__.py
custom_components/noaa_space_weather/api.py
custom_components/noaa_space_weather/binary_sensor.py
custom_components/noaa_space_weather/config_flow.py
custom_components/noaa_space_weather/const.py
custom_components/noaa_space_weather/manifest.json
custom_components/noaa_space_weather/sensor.py
custom_components/noaa_space_weather/switch.py
```

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[buymecoffee]: https://www.buymeacoffee.com/tcarwash
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/tcarwash/home-assistant_noaa-space-weather.svg?style=for-the-badge
[commits]: https://github.com/tcarwash/home-assistant_noaa-space-weather/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/tcarwash/home-assistant_noaa-space-weather.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40tcarwash-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/tcarwash/home-assistant_noaa-space-weather.svg?style=for-the-badge
[releases]: https://github.com/tcarwash/home-assistant_noaa-space-weather/releases
[user_profile]: https://github.com/tcarwash
