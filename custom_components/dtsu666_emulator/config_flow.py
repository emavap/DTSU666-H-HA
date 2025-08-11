"""Config flow for DTSU666 Emulator integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_UNIT_ID

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DTSU666 Emulator."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate port is not in use
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("localhost", user_input["port"]))
                sock.close()
                if result == 0:
                    errors["port"] = "port_in_use"
            except Exception:
                pass

            if not errors:
                await self.async_set_unique_id(f"dtsu666_{user_input['port']}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"DTSU666 Emulator (Port {user_input['port']})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_config_schema(),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/marcocamilli/dtsu666-emulator"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    def _get_config_schema(self, user_input: dict = None) -> vol.Schema:
        """Get the configuration schema."""
        if user_input is None:
            user_input = {}
            
        return vol.Schema({
            vol.Required("port", default=user_input.get("port", DEFAULT_PORT)): 
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=65535,
                        mode=selector.NumberSelectorMode.BOX
                    )
                ),
            vol.Required("unit_id", default=user_input.get("unit_id", DEFAULT_UNIT_ID)): 
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=247,
                        mode=selector.NumberSelectorMode.BOX
                    )
                ),
            vol.Optional("voltage_entity", default=user_input.get("voltage_entity")): 
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="voltage"
                    )
                ),
            vol.Optional("current_l1_entity", default=user_input.get("current_l1_entity")): 
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="current"
                    )
                ),
            vol.Optional("power_entity", default=user_input.get("power_entity")): 
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="power"
                    )
                ),
            vol.Optional("energy_import_entity", default=user_input.get("energy_import_entity")): 
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy"
                    )
                ),
            vol.Optional("energy_export_entity", default=user_input.get("energy_export_entity")): 
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy"
                    )
                ),
            vol.Optional("frequency_entity", default=user_input.get("frequency_entity")): 
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="frequency"
                    )
                ),
            vol.Optional("disable_validation", default=user_input.get("disable_validation", False)): 
                selector.BooleanSelector(),
        })


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for DTSU666 Emulator."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}
        
        if user_input is not None:
            # Validate port is not in use (unless it's the same port as current)
            current_port = self.config_entry.data.get("port", DEFAULT_PORT)
            new_port = user_input.get("port", current_port)
            
            if new_port != current_port:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(("localhost", new_port))
                    sock.close()
                    if result == 0:
                        errors["port"] = "port_in_use"
                except Exception:
                    pass
            
            if not errors:
                # Check if port has changed - need to update unique ID
                current_port = self.config_entry.data.get("port", DEFAULT_PORT)
                new_port = user_input.get("port", current_port)
                
                if new_port != current_port:
                    # Update the entry's unique ID for the new port
                    new_unique_id = f"dtsu666_{new_port}"
                    
                    # Check if another entry already has this unique ID
                    for entry in self.hass.config_entries.async_entries(DOMAIN):
                        if entry.unique_id == new_unique_id and entry != self.config_entry:
                            errors["port"] = "port_in_use"
                            break
                    
                    if not errors:
                        # Update unique ID
                        self.hass.config_entries.async_update_entry(
                            self.config_entry, unique_id=new_unique_id
                        )
                        
                        # Update title if port changed
                        new_title = f"DTSU666 Emulator (Port {new_port})"
                        self.hass.config_entries.async_update_entry(
                            self.config_entry, title=new_title
                        )
                
                if not errors:
                    return self.async_create_entry(title="", data=user_input)
            
            # If we have errors, fall through to show form again

        # Get current data, falling back to config data if no options exist
        current_data = {**self.config_entry.data, **self.config_entry.options}
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("port", default=current_data.get("port", DEFAULT_PORT)): 
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                vol.Required("unit_id", default=current_data.get("unit_id", DEFAULT_UNIT_ID)): 
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=247,
                            mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                vol.Optional("voltage_entity", default=current_data.get("voltage_entity")): 
                    selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="voltage"
                        )
                    ),
                vol.Optional("current_l1_entity", default=current_data.get("current_l1_entity")): 
                    selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="current"
                        )
                    ),
                vol.Optional("power_entity", default=current_data.get("power_entity")): 
                    selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="power"
                        )
                    ),
                vol.Optional("energy_import_entity", default=current_data.get("energy_import_entity")): 
                    selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="energy"
                        )
                    ),
                vol.Optional("energy_export_entity", default=current_data.get("energy_export_entity")): 
                    selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="energy"
                        )
                    ),
                vol.Optional("frequency_entity", default=current_data.get("frequency_entity")): 
                    selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="frequency"
                        )
                    ),
                vol.Optional("disable_validation", default=current_data.get("disable_validation", False)): 
                    selector.BooleanSelector(),
            }),
            errors=errors,
        )