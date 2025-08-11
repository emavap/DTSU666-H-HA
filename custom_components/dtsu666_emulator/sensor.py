"""Sensor platform for DTSU666 Emulator."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry  
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .modbus_server import DTSU666ModbusServer

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DTSU666 Emulator sensors from a config entry."""
    
    # Merge config data with options (options take precedence)
    config = {**config_entry.data, **config_entry.options}
    
    # Create and start the Modbus server
    server = DTSU666ModbusServer(hass, config)
    
    # Store server instance
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = server
    
    # Start server in background task
    asyncio.create_task(server.start())
    
    # Create status sensor
    sensor = DTSU666StatusSensor(config_entry, server)
    async_add_entities([sensor])

class DTSU666StatusSensor(SensorEntity):
    """Sensor showing DTSU666 emulator status."""
    
    def __init__(self, config_entry: ConfigEntry, server: DTSU666ModbusServer):
        """Initialize the sensor."""
        self._config_entry = config_entry
        self._server = server
        self._attr_name = f"DTSU666 Emulator Status (Port {config_entry.data['port']})"
        self._attr_unique_id = f"dtsu666_status_{config_entry.data['port']}"
        
    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self._server.server or getattr(self._server.server, 'is_closing', True):
            return "stopped"
            
        # Check entity validation status
        if not self._server._are_entities_valid():
            return "invalid_data"
            
        return "running"
        
    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        # Get current config (data + options)
        current_config = {**self._config_entry.data, **self._config_entry.options}
        
        attributes = {
            "port": current_config.get("port", "unknown"),
            "unit_id": current_config.get("unit_id", "unknown"),
            "entity_mappings": len([k for k, v in current_config.items() 
                                  if k.endswith("_entity") and v]),
            "validation_enabled": getattr(self._server, '_validation_enabled', True),
        }
        
        # Add entity validation details
        if hasattr(self._server, '_get_entity_validation_status'):
            validation_status = self._server._get_entity_validation_status()
            attributes["entity_status"] = validation_status
            
            # Count valid/invalid entities
            valid_count = sum(1 for status in validation_status.values() if status["valid"])
            total_count = len(validation_status)
            attributes["valid_entities"] = f"{valid_count}/{total_count}"
            
        return attributes
        
    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        if self.state == "running":
            return "mdi:check-network"
        elif self.state == "invalid_data":
            return "mdi:alert-network"
        else:
            return "mdi:network-off"