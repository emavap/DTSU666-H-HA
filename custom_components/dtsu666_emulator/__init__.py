"""DTSU666 Emulator integration for Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

DOMAIN = "dtsu666_emulator"
PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DTSU666 Emulator from a config entry."""
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Stop the Modbus server if it exists
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        server = hass.data[DOMAIN][entry.entry_id]
        await server.stop()
        del hass.data[DOMAIN][entry.entry_id]
    
    return unload_ok

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # Update the server configuration with new options
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        server = hass.data[DOMAIN][entry.entry_id]
        # Merge entry data with options (options take precedence)
        new_config = {**entry.data, **entry.options}
        
        # Check if network settings (port/unit_id) have changed
        current_config = server.config
        needs_restart = (
            new_config.get("port") != current_config.get("port") or
            new_config.get("unit_id") != current_config.get("unit_id")
        )
        
        if needs_restart:
            # Stop current server
            await server.stop()
            
            # Update configuration
            server.update_config(new_config)
            
            # Restart server with new settings
            import asyncio
            asyncio.create_task(server.start())
        else:
            # Only update entity mappings
            server.update_config(new_config)