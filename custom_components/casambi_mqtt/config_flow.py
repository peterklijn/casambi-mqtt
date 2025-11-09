from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

import voluptuous as vol
from homeassistant.core import callback

from homeassistant import config_entries

from .const import CONF_NETWORK_NAME, DEFAULT_NETWORK_NAME, DOMAIN


class CasambiMqttConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Casambi MQTT config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Save configuration and create entry
            return self.async_create_entry(
                title=user_input[CONF_NETWORK_NAME],
                data={CONF_NETWORK_NAME: user_input[CONF_NETWORK_NAME]},
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NETWORK_NAME, default=DEFAULT_NETWORK_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler for updating configuration."""
        return CasambiMqttOptionsFlow(entry)


class CasambiMqttOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Casambi MQTT integration."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            # Update the entry with the new network name
            return self.async_create_entry(
                title="THISI STHE TITLE!",
                data={CONF_NETWORK_NAME: user_input[CONF_NETWORK_NAME]},
            )

        current_name: str = (
            self.entry.options.get(CONF_NETWORK_NAME)
            or self.entry.data.get(CONF_NETWORK_NAME)
            or DEFAULT_NETWORK_NAME
        )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NETWORK_NAME, default=current_name): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "restart_note": "Restart Home Assistant after changing this value"
            },
        )
