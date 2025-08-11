"""Constants for the DTSU666 Emulator integration."""

DOMAIN = "dtsu666_emulator"

# Default configuration values
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_UPDATE_INTERVAL = 1  # 1 second, matching original device

# DTSU666-H Modbus register map based on VERIFIED GitHub implementation
# Source: https://github.com/elfabriceu/DTSU666-Modbus/blob/main/plugin.py (WORKING CODE)
# Cross-verified with: Home Assistant Community, Tasmota discussions
# NOTE: All registers use float32 format with specific scaling as per working implementation
DTSU666_REGISTERS = {
    # Voltage measurements - Line-to-Neutral (FP32, divide by 10)
    "voltage_l1": {"address": 0x2006, "type": "float32", "scale": 10.0, "unit": "V"},     # Voltage L1 (verified working)
    "voltage_l2": {"address": 0x2008, "type": "float32", "scale": 10.0, "unit": "V"},     # Voltage L2 (verified working)  
    "voltage_l3": {"address": 0x200A, "type": "float32", "scale": 10.0, "unit": "V"},     # Voltage L3 (verified working)
    
    # Current measurements - FP32 format, divide by 1000 (verified from working code)
    "current_l1": {"address": 0x200C, "type": "float32", "scale": 1000.0, "unit": "A"},   # Current L1 (verified working)
    "current_l2": {"address": 0x200E, "type": "float32", "scale": 1000.0, "unit": "A"},   # Current L2 (verified working)
    "current_l3": {"address": 0x2010, "type": "float32", "scale": 1000.0, "unit": "A"},   # Current L3 (verified working)
    
    # Power measurements - FP32 format, divide by 10 (verified from working implementation)
    "active_power": {"address": 0x2012, "type": "float32", "scale": 10.0, "unit": "W"},      # Total System Active Power (verified)
    "reactive_power": {"address": 0x201A, "type": "float32", "scale": 10.0, "unit": "var"},  # Total System Reactive Power (verified)
    "apparent_power": {"address": 0x2022, "type": "float32", "scale": 10.0, "unit": "VA"},   # Total System Apparent Power (calculated)
    
    # Power factor - FP32 format, divide by 1000 (verified from working code)
    "power_factor": {"address": 0x202A, "type": "float32", "scale": 1000.0, "unit": ""},    # Total System Power Factor (verified)
    
    # Frequency - FP32 format, divide by 100 (verified from working implementation)
    "frequency": {"address": 0x2044, "type": "float32", "scale": 100.0, "unit": "Hz"},      # Frequency of Supply Voltages (verified)
    
    # Energy measurements - FP32 format, multiply by 1000 (verified from working code)  
    "energy_import": {"address": 0x401E, "type": "float32", "scale": 0.001, "unit": "kWh"}, # Total Import kWh (verified)
    "energy_export": {"address": 0x4028, "type": "float32", "scale": 0.001, "unit": "kWh"}, # Total Export kWh (verified)
    "reactive_energy_import": {"address": 0x4032, "type": "float32", "scale": 0.001, "unit": "kvarh"}, # Q1 kVArh (verified)
    "reactive_energy_export": {"address": 0x403C, "type": "float32", "scale": 0.001, "unit": "kvarh"},  # Q2 kVArh (verified)
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