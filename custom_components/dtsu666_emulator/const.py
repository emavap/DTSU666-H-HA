"""Constants for the DTSU666 Emulator integration."""

DOMAIN = "dtsu666_emulator"

# Default configuration values
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_UPDATE_INTERVAL = 1  # 1 second, matching original device

# DTSU666-H Modbus register map based on verified community sources (2024-2025)
# Primary source: Home Assistant Community discussion with confirmed working addresses
# Note: DTSU666-H uses FP32 (float32) format for most registers
DTSU666_REGISTERS = {
    # Voltage measurements - FP32 format, direct in Volts (confirmed from community)
    "voltage_l1": {"address": 0x2000, "type": "float32", "scale": 1.0, "unit": "V"},
    "voltage_l2": {"address": 0x2006, "type": "float32", "scale": 1.0, "unit": "V"},  
    "voltage_l3": {"address": 0x2008, "type": "float32", "scale": 1.0, "unit": "V"},  
    
    # Current measurements - FP32 format, direct in Amperes (confirmed from community)
    "current_l1": {"address": 0x2002, "type": "float32", "scale": 1.0, "unit": "A"},  # Verified working address
    "current_l2": {"address": 0x200A, "type": "float32", "scale": 1.0, "unit": "A"},  
    "current_l3": {"address": 0x200C, "type": "float32", "scale": 1.0, "unit": "A"},  
    
    # Power measurements - FP32 format with community-verified scaling
    "active_power": {"address": 0x2004, "type": "float32", "scale": 1000.0, "unit": "W"},  # multiply by 1000 (verified)
    "reactive_power": {"address": 0x2012, "type": "float32", "scale": 1000.0, "unit": "var"},  # multiply by 1000 (verified)
    "apparent_power": {"address": 0x2014, "type": "float32", "scale": 1000.0, "unit": "VA"},
    
    # Power factor - FP32 format, direct value
    "power_factor": {"address": 0x2016, "type": "float32", "scale": 1.0, "unit": ""},
    
    # Frequency - FP32 format, direct in Hz (confirmed address)
    "frequency": {"address": 0x200E, "type": "float32", "scale": 1.0, "unit": "Hz"},
    
    # Energy measurements - FP32 format, direct in kWh (confirmed addresses)
    "energy_import": {"address": 0x400A, "type": "float32", "scale": 1.0, "unit": "kWh"},  # Energy Purchased (verified)
    "energy_export": {"address": 0x4000, "type": "float32", "scale": 1.0, "unit": "kWh"},   # Energy Sold (verified)
    "reactive_energy_import": {"address": 0x401A, "type": "float32", "scale": 1.0, "unit": "kvarh"},
    "reactive_energy_export": {"address": 0x4010, "type": "float32", "scale": 1.0, "unit": "kvarh"},
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