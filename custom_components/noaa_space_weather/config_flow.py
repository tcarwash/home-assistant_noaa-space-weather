"""Config flow to configure the NOAA Space Weather integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING, DEFAULT_NAME, DOMAIN


class NoaaSpaceWeatherConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for NOAA Space Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # Store config in options to make it editable later via options flow
            options = {
                CONF_LEGACY_NAMING: user_input.get(
                    CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
                )
            }
            return self.async_create_entry(title=DEFAULT_NAME, data={}, options=options)

        schema = vol.Schema(
            {
                vol.Optional(CONF_LEGACY_NAMING, default=DEFAULT_LEGACY_NAMING): bool,
            }
        )
        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation_url": "https://github.com/tcarwash/home-assistant_noaa-space-weather"
            },
            data_schema=schema,
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return NoaaSpaceWeatherOptionsFlowHandler(config_entry)


class NoaaSpaceWeatherOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_LEGACY_NAMING,
                    default=self.config_entry.options.get(
                        CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
                    ),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
