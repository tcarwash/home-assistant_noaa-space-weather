"""Test NOAA Space Weather setup and image platform lifecycle."""

import base64
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers.entity_component import DATA_INSTANCES
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.noaa_space_weather import NoaaSpaceWeatherDataUpdateCoordinator
from custom_components.noaa_space_weather.const import DOMAIN


async def test_setup_unload_and_reload_entry(hass, bypass_get_data):
    """Test config entry setup, reload, and unload through Home Assistant."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={"sensor": False, "image": False},
        entry_id="test",
    )
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        is NoaaSpaceWeatherDataUpdateCoordinator
    )

    assert await hass.config_entries.async_reload(config_entry.entry_id)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        is NoaaSpaceWeatherDataUpdateCoordinator
    )

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass, error_on_get_data):
    """Test that a failed initial update schedules a setup retry."""
    config_entry = MockConfigEntry(domain=DOMAIN, data={}, entry_id="test")
    config_entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_image_platform_loads_and_unloads(hass, bypass_get_data):
    """Test image entity setup and background task cleanup on unload."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={"sensor": False},
        entry_id="image-test",
    )
    config_entry.add_to_hass(hass)
    first_frame = base64.b64decode(
        "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    )

    with (
        patch(
            "custom_components.noaa_space_weather.api.NoaaSpaceWeatherApiClient.async_get_first_frame",
            new=AsyncMock(return_value=first_frame),
        ),
        patch(
            "custom_components.noaa_space_weather.api.NoaaSpaceWeatherApiClient.async_prefetch_animations",
            new=AsyncMock(return_value=None),
        ),
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        image_ids = hass.states.async_entity_ids("image")
        assert len(image_ids) == 17
        animation_id = next(
            entity_id for entity_id in image_ids if "animated" in entity_id
        )
        image_entity = hass.data[DATA_INSTANCES]["image"].get_entity(animation_id)
        assert image_entity is not None
        assert await image_entity.async_image() == first_frame
        assert await hass.config_entries.async_unload(config_entry.entry_id)
