"""Modbus TCP Server emulating DTSU666-H power meter."""
from __future__ import annotations

import asyncio
import logging
import struct
from typing import Any, Dict

# Import compatibility for different pymodbus versions
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# Handle ModbusSlaveContext vs ModbusDeviceContext change in 3.10+
try:
    from pymodbus.datastore import ModbusSlaveContext
    DEVICE_CONTEXT_CLASS = ModbusSlaveContext
    DEVICE_CONTEXT_PARAM = "slaves"
except ImportError:
    from pymodbus.datastore import ModbusDeviceContext
    DEVICE_CONTEXT_CLASS = ModbusDeviceContext  
    DEVICE_CONTEXT_PARAM = "device_ids"
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
# Handle ModbusExceptions vs ModbusException naming change
try:
    from pymodbus.pdu import ModbusExceptions
    SERVER_DEVICE_FAILURE = ModbusExceptions.ServerDeviceFailure
except ImportError:
    # In newer versions, use the constants directly
    SERVER_DEVICE_FAILURE = 4  # ServerDeviceFailure error code

# Handle server imports - pymodbus 3.6+ moved these from server.async_io to server
try:
    from pymodbus.server import ModbusTcpServer, ModbusConnectedRequestHandler
except ImportError:
    from pymodbus.server.async_io import ModbusTcpServer, ModbusConnectedRequestHandler

# Handle optional interfaces import for older versions
try:
    from pymodbus.interfaces import IModbusSlaveContext
except ImportError:
    # Not needed in newer versions
    IModbusSlaveContext = None

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.event import async_track_state_change_event

from .const import DTSU666_REGISTERS

_LOGGER = logging.getLogger(__name__)

class ValidatedModbusRequestHandler(ModbusConnectedRequestHandler):
    """Custom request handler that validates entity data before processing."""
    
    def __init__(self, server_instance, *args, **kwargs):
        """Initialize the validated request handler."""
        super().__init__(*args, **kwargs)
        self.server_instance = server_instance
    
    async def execute(self, request, *addr):
        """Execute request only if entities are valid."""
        # Check if entities are valid before processing any request
        if hasattr(self.server_instance, '_are_entities_valid') and not self.server_instance._are_entities_valid():
            _LOGGER.warning("Rejecting Modbus request - entities have invalid data")
            # Return server device failure exception
            request.ExceptionCode = SERVER_DEVICE_FAILURE
            return request
        
        # Process request normally if entities are valid
        return await super().execute(request, *addr)

class ValidatedModbusSlaveContext(DEVICE_CONTEXT_CLASS):
    """Custom Modbus slave context that validates entity data before responding."""
    
    def __init__(self, server_instance, *args, **kwargs):
        """Initialize the validated slave context."""
        super().__init__(*args, **kwargs)
        self.server_instance = server_instance
        
    def validate(self, fc_as_hex, address, count=1):
        """Validate that all required entities have valid data."""
        if not self.server_instance._are_entities_valid():
            _LOGGER.debug("Modbus validation failed - entities have invalid data")
            return False
        return super().validate(fc_as_hex, address, count)

class DTSU666ModbusServer:
    """DTSU666-H Modbus TCP Server emulation."""
    
    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the Modbus server."""
        self.hass = hass
        self.config = config
        self.server = None
        self.context = None
        self._entity_mappings = {}
        self._entity_states = {}  # Track current entity states
        self._validation_enabled = not config.get("disable_validation", False)
        self._setup_entity_mappings()
        
    def _setup_entity_mappings(self):
        """Setup entity mappings from config."""
        mappings = {
            "voltage_entity": "voltage_l1",
            "current_l1_entity": "current_l1", 
            "power_entity": "output_power",
            "energy_import_entity": "energy_consumed_main",
            "energy_export_entity": "energy_injected_main",
            "frequency_entity": "frequency",
        }
        
        for config_key, register_key in mappings.items():
            entity_id = self.config.get(config_key)
            if entity_id:
                self._entity_mappings[entity_id] = register_key
                
    def update_config(self, new_config: dict):
        """Update configuration and entity mappings."""
        self.config.update(new_config)
        self._entity_mappings.clear()
        self._setup_entity_mappings()
        
        # Re-setup state tracking with new entities (only if server is running)
        if hasattr(self, '_unsub_state_tracking') and self._unsub_state_tracking:
            self._unsub_state_tracking()
            self._unsub_state_tracking = None
            
        # Only restart state tracking if we have a running server
        if self.server and not getattr(self.server, 'is_closing', True):
            asyncio.create_task(self._setup_state_tracking())
    
    def _are_entities_valid(self) -> bool:
        """Check if all configured entities have valid data."""
        if not self._validation_enabled:
            return True
            
        if not self._entity_mappings:
            # No entities configured, use default values
            return True
            
        for entity_id in self._entity_mappings.keys():
            state = self.hass.states.get(entity_id)
            if not self._is_entity_state_valid(state):
                _LOGGER.debug("Entity %s has invalid state: %s", entity_id, 
                            state.state if state else "None")
                return False
        
        return True
    
    def _is_entity_state_valid(self, state: State | None) -> bool:
        """Check if a single entity state is valid."""
        if state is None:
            return False
            
        if state.state in ("unknown", "unavailable", "None", None):
            return False
            
        # Try to convert to float
        try:
            float(state.state)
            return True
        except (ValueError, TypeError):
            return False
    
    def _get_entity_validation_status(self) -> dict:
        """Get validation status for all entities."""
        status = {}
        for entity_id in self._entity_mappings.keys():
            state = self.hass.states.get(entity_id)
            status[entity_id] = {
                "valid": self._is_entity_state_valid(state),
                "state": state.state if state else "None",
                "register": self._entity_mappings[entity_id]
            }
        return status
    
    async def start(self):
        """Start the Modbus TCP server."""
        try:
            # Initialize data blocks for different register ranges
            holding_registers = ModbusSequentialDataBlock(0x0000, [0] * 0x5000)
            
            # Setup validated slave context that checks entity validity
            # Handle parameter changes in newer pymodbus versions
            context_params = {
                "di": None,  # Discrete inputs
                "co": None,  # Coils
                "hr": holding_registers,  # Holding registers
                "ir": holding_registers   # Input registers (same as holding for this device)
            }
            
            try:
                # Try with older parameters that may have been removed
                slave_context = ValidatedModbusSlaveContext(
                    self,  # Pass server instance for validation
                    **context_params
                )
            except TypeError:
                # If that fails, try without deprecated parameters
                slave_context = ValidatedModbusSlaveContext(
                    self,  # Pass server instance for validation 
                    **context_params
                )
            
            # Setup server context - handle API parameter change
            context_kwargs = {DEVICE_CONTEXT_PARAM: {self.config["unit_id"]: slave_context}, "single": False}
            self.context = ModbusServerContext(**context_kwargs)
            
            # Device identification
            identity = ModbusDeviceIdentification()
            identity.VendorName = "Huawei"
            identity.ProductCode = "DTSU666-H"
            identity.VendorUrl = "https://www.huawei.com"
            identity.ProductName = "DTSU666-H Smart Power Sensor"
            identity.ModelName = "DTSU666-H"
            identity.MajorMinorRevision = "1.0"
            
            # Create server - handle API changes for handler parameter  
            try:
                # Try older API with handler parameter (pre-3.4.0)
                server_instance = self
                
                class DTSU666RequestHandler(ValidatedModbusRequestHandler):
                    def __init__(self, *args, **kwargs):
                        super().__init__(server_instance, *args, **kwargs)
                
                self.server = ModbusTcpServer(
                    context=self.context,
                    identity=identity,
                    address=("0.0.0.0", self.config["port"]),
                    handler=DTSU666RequestHandler
                )
            except TypeError:
                # Newer API without handler parameter (3.4.0+)
                self.server = ModbusTcpServer(
                    context=self.context,
                    identity=identity,
                    address=("0.0.0.0", self.config["port"])
                )
                _LOGGER.warning("Using newer pymodbus API - custom validation handler not available")
            
            # Initialize default values
            await self._initialize_registers()
            
            # Setup state tracking
            await self._setup_state_tracking()
            
            # Start server
            await self.server.serve_forever()
            _LOGGER.info("DTSU666 Modbus server started on port %s", self.config["port"])
            
        except Exception as e:
            _LOGGER.error("Failed to start Modbus server: %s", e)
            raise
    
    async def stop(self):
        """Stop the Modbus server."""
        # Unsubscribe from state tracking
        if hasattr(self, '_unsub_state_tracking') and self._unsub_state_tracking:
            self._unsub_state_tracking()
            self._unsub_state_tracking = None
            
        if self.server:
            try:
                await self.server.shutdown()
                _LOGGER.info("DTSU666 Modbus server stopped")
            except Exception as e:
                _LOGGER.warning("Error stopping Modbus server: %s", e)
            finally:
                self.server = None
    
    async def _initialize_registers(self):
        """Initialize registers with default values."""
        slave_id = self.config["unit_id"]
        
        # Set default values for EXACT registers from GitHub implementation
        defaults = {
            # From JsonEntry array
            "frequency": 50.0,
            "voltage_l1": 230.0,
            "voltage_l2": 230.0, 
            "voltage_l3": 230.0,
            "current_l1": 0.0,
            "current_l2": 0.0,
            "current_l3": 0.0,
            "output_power": 0.0,
            "active_power_l1": 0.0,
            "active_power_l2": 0.0,
            "active_power_l3": 0.0,
            
            # Energy registers from setReg calls
            "energy_consumed_main": 0.0,
            "energy_injected_main": 0.0,
            "energy_consumed_alt": 0.0,
            "energy_injected_alt": 0.0,
        }
        
        for register_name, default_value in defaults.items():
            await self._update_register(register_name, default_value)
    
    async def _setup_state_tracking(self):
        """Setup state tracking for configured entities."""
        if not self._entity_mappings:
            return
            
        # Track state changes for mapped entities
        self._unsub_state_tracking = async_track_state_change_event(
            self.hass, 
            list(self._entity_mappings.keys()),
            self._state_changed_callback
        )
        
        # Initialize with current states
        for entity_id in self._entity_mappings.keys():
            state = self.hass.states.get(entity_id)
            if state:
                await self._process_state_change(entity_id, state)
    
    async def _state_changed_callback(self, event):
        """Handle state changes for tracked entities."""
        entity_id = event.data["entity_id"]
        new_state = event.data.get("new_state")
        
        if new_state and entity_id in self._entity_mappings:
            await self._process_state_change(entity_id, new_state)
    
    async def _process_state_change(self, entity_id: str, state: State):
        """Process state change and update corresponding register."""
        try:
            register_name = self._entity_mappings[entity_id]
            
            # Update entity states tracking
            self._entity_states[entity_id] = state
            
            # Check if state is valid
            if not self._is_entity_state_valid(state):
                _LOGGER.info("Entity %s now has invalid state: %s", entity_id, state.state)
                return
                
            value = float(state.state)
            await self._update_register(register_name, value)
            
        except (ValueError, TypeError) as e:
            _LOGGER.warning("Failed to process state change for %s: %s", entity_id, e)
    
    async def _update_register(self, register_name: str, value: float):
        """Update a specific register with new value."""
        if register_name not in DTSU666_REGISTERS:
            return
            
        register_info = DTSU666_REGISTERS[register_name]
        address = register_info["address"]
        reg_type = register_info["type"]
        scale = register_info.get("scale", 1.0)
        
        # Scale the value (multiply by scale factor as per DTSU666 implementation)
        scaled_value = value * scale
        
        try:
            # Convert to appropriate data type and write to registers
            if reg_type == "float32":
                # Convert to 32-bit float and split into 2 registers
                builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
                builder.add_32bit_float(scaled_value)
                payload = builder.to_registers()
                
                self.context[self.config["unit_id"]].setValues(3, address, payload)
                
            elif reg_type == "int32":
                # Convert to 32-bit int and split into 2 registers  
                int_value = int(scaled_value)
                builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
                builder.add_32bit_int(int_value)
                payload = builder.to_registers()
                
                self.context[self.config["unit_id"]].setValues(3, address, payload)
                
            elif reg_type == "int16":
                # Convert to 16-bit int (single register)
                int_value = int(scaled_value) & 0xFFFF
                self.context[self.config["unit_id"]].setValues(3, address, [int_value])
                
            elif reg_type == "int64":
                # Convert to 64-bit int and split into 4 registers
                int_value = int(scaled_value)
                builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
                builder.add_64bit_int(int_value)
                payload = builder.to_registers()
                
                self.context[self.config["unit_id"]].setValues(3, address, payload)
                
        except Exception as e:
            _LOGGER.error("Failed to update register %s: %s", register_name, e)