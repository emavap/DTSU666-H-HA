"""Constants for the DTSU666 Emulator integration."""

DOMAIN = "dtsu666_emulator"

# Default configuration values
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_UPDATE_INTERVAL = 1  # 1 second, matching original device

# DTSU666-H Modbus register map based on research
DTSU666_REGISTERS = {
    # Voltage measurements (3-phase)
    "voltage_l1": {"address": 0x2000, "type": "float32", "scale": 0.1, "unit": "V"},
    "voltage_l2": {"address": 0x2002, "type": "float32", "scale": 0.1, "unit": "V"},
    "voltage_l3": {"address": 0x2004, "type": "float32", "scale": 0.1, "unit": "V"},
    
    # Current measurements (3-phase)
    "current_l1": {"address": 0x2008, "type": "float32", "scale": 0.001, "unit": "A"},
    "current_l2": {"address": 0x200A, "type": "float32", "scale": 0.001, "unit": "A"},
    "current_l3": {"address": 0x200C, "type": "float32", "scale": 0.001, "unit": "A"},
    
    # Power measurements
    "active_power": {"address": 0x2010, "type": "int32", "scale": 0.001, "unit": "kW"},
    "reactive_power": {"address": 0x2014, "type": "int32", "scale": 0.001, "unit": "kvar"},
    "apparent_power": {"address": 0x2018, "type": "int32", "scale": 0.001, "unit": "kVA"},
    
    # Power factor
    "power_factor": {"address": 0x201C, "type": "int16", "scale": 0.001, "unit": ""},
    
    # Frequency
    "frequency": {"address": 0x200E, "type": "int16", "scale": 0.01, "unit": "Hz"},
    
    # Energy measurements
    "energy_import": {"address": 0x4000, "type": "int64", "scale": 0.01, "unit": "kWh"},
    "energy_export": {"address": 0x400A, "type": "int64", "scale": 0.01, "unit": "kWh"},
    "reactive_energy_import": {"address": 0x4020, "type": "int64", "scale": 0.01, "unit": "kvarh"},
    "reactive_energy_export": {"address": 0x4030, "type": "int64", "scale": 0.01, "unit": "kvarh"},
}

# Entity mapping keys
ENTITY_MAPPINGS = [
    "voltage_entity",
    "current_l1_entity", 
    "current_l2_entity",
    "current_l3_entity",
    "power_entity",
    "energy_import_entity",
    "energy_export_entity",
    "frequency_entity",
]