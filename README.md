# NOAA Space Weather

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

A Home Assistant custom integration for the NOAA Space Weather Prediction Center (SWPC).

This project is community-maintained and not affiliated with NOAA.

![example][exampleimg]

## Features

- Sensors for common space-weather indices and probabilities
- Image entities for static SWPC products
- Animation/image entities for SUVI, LASCO, Geospace, Ovation aurora, and more
- UI-only setup with an option to keep legacy entity IDs

### Platforms

- sensor: numeric indices and probabilities
- image: static images and animated products (GIFs)

### Available sensors

The following sensors are created (names shown are the friendly names):

- Solar Flux Index
- A Index
- A Index 2 Day
- A Index 3 Day
- Planetary K-Index (uses estimated Kp when available)
- Sunspot Number
- Polar Cap Absorption
- X-Class 1 Day Probability
- M-Class 1 Day Probability

Entity IDs are derived from the friendly names. By default they include a prefix `noaasw_` (configurable, see Options below). For example:

- sensor.noaasw_solar_flux_index
- sensor.noaasw_planetary_k_index
- sensor.noaasw_sunspot_number

If you enable Legacy naming, the prefix is removed (e.g., `sensor.solar_flux_index`).

### Image and animation entities

The integration exposes several image entities (domain: `image`). Animated products render as GIFs when possible and fall back to a static frame if needed.

Animated products include:

- Animated SUVI Secondary 284 Å
- Animated SUVI Primary 171 Å
- Animated SUVI Primary 304 Å
- Animated SUVI Thematic Map
- Animated WFS Ionosphere
- Animated Coronagraph CCOR1
- Animated Lasco C2
- Animated Lasco C3
- Animated Geospace Magnetosphere Velocity
- Animated Geospace Magnetosphere Density
- Animated Geospace Magnetosphere Pressure
- Animated Aurora Forecast North (24h)
- Animated Aurora Forecast South (24h)
- Animated Geoelectric Field US-Canada (1D)

Static image products include:

- ACE Solar Wind (3 hour)
- Today's forecasted aurora viewline (experimental)
- Tomorrow's forecasted aurora viewline (experimental)

Tip: Use the Picture Entity or Image card in Lovelace to display these.

## Installation

### HACS (Custom Repository)

1. In HACS, go to Integrations → three-dots menu → Custom repositories
2. Add this repository URL and select category “Integration”
3. Install “NOAA Space Weather” from HACS
4. Restart Home Assistant
5. Add the integration in Settings → Devices & Services → Add Integration → search “NOAA Space Weather”

<<<<<<< HEAD

### Manual

1. Open your Home Assistant config directory (where `configuration.yaml` lives)
2. Create `custom_components/noaa_space_weather/` if it doesn’t exist
3. Copy the contents of `custom_components/noaa_space_weather/` from this repo into that folder
4. Restart Home Assistant
5. Add the integration via Settings → Devices & Services

## Configuration (UI)

During setup you can choose:

- Legacy naming: When enabled, entity IDs won’t be prefixed. This helps preserve older dashboards/automations; when disabled (default), entity IDs are prefixed with `noaasw_` to avoid conflicts.

You can change this later under the integration’s Options.

## Using the entities

Example Lovelace snippets:

Picture Entity showing an animated product:

````yaml
type: picture-entity
entity: image.noaasw_animated_suvi_primary_171_angstroms
show_state: false
show_name: true
=======
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
>>>>>>> 604870215908b8c2f735dba5190982a8dcf08429
````

Entities card with key sensors:

```yaml
type: entities
entities:
  - sensor.noaasw_planetary_k_index
  - sensor.noaasw_solar_flux_index
  - sensor.noaasw_sunspot_number
  - sensor.noaasw_x_class_1_day_probability
  - sensor.noaasw_m_class_1_day_probability
```

Note: Exact entity IDs depend on your naming option (legacy vs. prefixed) and may vary slightly if Home Assistant adjusts slugs.

## Troubleshooting

- Animations take a bit to appear: Frames are prefetched and cached after setup; a static first frame may show before the full GIF is ready.
- Some products can be slow or occasionally unavailable from SWPC. The integration falls back gracefully.
- If entity IDs changed after upgrading, toggle Legacy naming in Options, or update dashboards to the new prefixed IDs.

## Contributions

PRs and issues are welcome. See the [Contribution guidelines](CONTRIBUTING.md).

## Credits

- Built on top of the amazing [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component)
- Inspired by [integration_blueprint][integration_blueprint]

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
