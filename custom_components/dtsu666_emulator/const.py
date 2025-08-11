"""Constants for the DTSU666 Emulator integration."""

DOMAIN = "dtsu666_emulator"

# Default configuration values
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_UPDATE_INTERVAL = 1  # 1 second, matching original device

# DTSU666 Huawei Modbus register map 
# Source: https://github.com/rdu70/P1-2-DTSU666 (verified Huawei DTSU666 implementation)
# Device: DTSU666 (Huawei variant with verified register addresses)
# Communication: Modbus RTU, RS485
DTSU666_REGISTERS = {
    # EXACT register mapping from GitHub rdu70/P1-2-DTSU666 JsonEntry array
    "frequency": {"address": 0x2044, "type": "int16", "scale": 100.0, "unit": "Hz"},              # GridFrequency (EXACT from JsonEntry)
    "voltage_l1": {"address": 0x2006, "type": "int16", "scale": 10.0, "unit": "V"},              # L1ThreePhaseGridVoltage (EXACT from JsonEntry)
    "voltage_l2": {"address": 0x2008, "type": "int16", "scale": 10.0, "unit": "V"},              # L2ThreePhaseGridVoltage (EXACT from JsonEntry)
    "voltage_l3": {"address": 0x200A, "type": "int16", "scale": 10.0, "unit": "V"},              # L3ThreePhaseGridVoltage (EXACT from JsonEntry)
    "current_l1": {"address": 0x200C, "type": "int16", "scale": 1000.0, "unit": "A"},           # L1ThreePhaseGridOutputCurrent (EXACT from JsonEntry)
    "current_l2": {"address": 0x200E, "type": "int16", "scale": 1000.0, "unit": "A"},           # L2ThreePhaseGridOutputCurrent (EXACT from JsonEntry)
    "current_l3": {"address": 0x2010, "type": "int16", "scale": 1000.0, "unit": "A"},           # L3ThreePhaseGridOutputCurrent (EXACT from JsonEntry)
    "output_power": {"address": 0x2012, "type": "int16", "scale": 10.0, "unit": "W"},           # OutputPower (EXACT from JsonEntry)
    "active_power_l1": {"address": 0x2014, "type": "int16", "scale": 10.0, "unit": "W"},        # L1ThreePhaseGridOutputPower (EXACT from JsonEntry)
    "active_power_l2": {"address": 0x2016, "type": "int16", "scale": 10.0, "unit": "W"},        # L2ThreePhaseGridOutputPower (EXACT from JsonEntry)
    "active_power_l3": {"address": 0x2018, "type": "int16", "scale": 10.0, "unit": "W"},        # L3ThreePhaseGridOutputPower (EXACT from JsonEntry)
    
    # Energy registers from the setReg calls (EXACT from source code)
    "energy_consumed_main": {"address": 0x401E, "type": "int16", "scale": 0.1, "unit": "kWh"},   # PV.setReg(0x401e,10.0 * dg.E_consumed/100.0)
    "energy_injected_main": {"address": 0x4028, "type": "int16", "scale": 0.1, "unit": "kWh"},   # PV.setReg(0x4028,10.0 * dg.E_injected/100.0)
    "energy_consumed_alt": {"address": 0x101E, "type": "int16", "scale": 0.1, "unit": "kWh"},    # PV.setReg(0x101e,10.0 * dg.E_consumed/100.0)
    "energy_injected_alt": {"address": 0x1028, "type": "int16", "scale": 0.1, "unit": "kWh"},    # PV.setReg(0x1028,10.0 * dg.E_injected/100.0)
    
    # NOTE: This uses ONLY the exact register addresses and scaling from the GitHub source code
    # No assumptions or additions - these are the registers actually implemented in the source
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