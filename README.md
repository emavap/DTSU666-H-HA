# DTSU666 Emulator for Home Assistant

This Home Assistant custom integration emulates a Huawei DTSU666 power meter via Modbus TCP using verified register mapping. It allows you to use real values from your Home Assistant entities instead of fake values, making it perfect for testing and development scenarios with Huawei inverters.

## Features

- **Verified DTSU666 Register Map**: Uses the correct Modbus register addresses and data types from verified Huawei DTSU666 implementation
- **Real Data Integration**: Maps Home Assistant sensor entities to corresponding power meter registers
- **Proper Refresh Rate**: Matches the original device's 1-second update interval
- **Single-Phase Support**: Supports voltage, current, power, energy, and frequency measurements for single-phase systems
- **Entity Validation**: Like real meters, rejects connections when entities have invalid data (unknown/unavailable)
- **Easy Configuration**: Simple config flow setup through Home Assistant UI with full reconfigurability

## Supported Measurements

The emulator supports all standard DTSU666-FE single-phase measurements:

- **Voltage**: Single-phase voltage (230V AC typical)
- **Current**: Single-phase current measurement
- **Power**: Active, reactive, and apparent power
- **Energy**: Import and export energy counters
- **Power Factor**: Power factor measurement
- **Frequency**: Grid frequency (50/60Hz)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/marcocamilli/dtsu666-emulator`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "DTSU666 Emulator" and install

### Manual Installation

1. Download this repository
2. Copy the `custom_components/dtsu666_emulator` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Initial Setup
1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "DTSU666 Emulator"
4. Configure the following:
   - **Port**: Modbus TCP port (default: 502)
   - **Unit ID**: Modbus unit ID (default: 1)
   - **Entity Mappings**: Select Home Assistant entities to map to each register:
     - Voltage Entity (Single Phase)
     - Current Entity (Single Phase)
     - Power Entity
     - Energy Import/Export Entities
     - Frequency Entity
     - Reactive Power Entity
     - Power Factor Entity

### Reconfiguration (Post-Installation)
1. Go to Settings → Devices & Services
2. Find your "DTSU666 Emulator" integration
3. Click "Configure"
4. **All settings can be changed**:
   - **Port & Unit ID**: Changes automatically restart the Modbus server
   - **Entity Mappings**: Changes take effect immediately
   - **Entity Validation**: Enable/disable validation that rejects connections when entities are invalid
   - **Real-time Updates**: No integration reload required

## Usage

Once configured, the integration will:

1. Start a Modbus TCP server on the specified port
2. Monitor the configured Home Assistant entities
3. Update the corresponding DTSU666-H registers in real-time
4. Provide a status sensor showing the emulator state

External Modbus clients (like Huawei inverters or monitoring systems) can then connect to this emulated DTSU666-H device and read the real data from your Home Assistant entities.

## Entity Validation

**By default, the emulator behaves like a real DTSU666-H meter**:
- **Invalid Entity Data**: If any configured entity has `unknown`, `unavailable`, or non-numeric values, the server will reject all Modbus connections
- **Connection Rejection**: Clients receive `ServerDeviceFailure` exceptions when attempting to read from an "offline" meter
- **Real-time Monitoring**: The status sensor shows `invalid_data` when entities are invalid
- **Validation Override**: Can be disabled via "Disable Entity Validation" option for testing

**Entity States Considered Invalid**:
- `unknown` - Entity exists but state is unknown
- `unavailable` - Entity is temporarily unavailable  
- `None` or empty values
- Non-numeric strings that can't be converted to float

This ensures the emulator provides realistic behavior matching real hardware failures.

## Register Map

The integration uses the **DTSU666 Huawei register map** based on verified implementation:

| Register | Address | Type | Description | Unit | Scale Factor |
|----------|---------|------|-------------|------|-------------|
| Grid Frequency | 0x2044 | int16 | Grid Frequency | Hz | ×100 |
| L1 Voltage | 0x2006 | int16 | L1 Three-Phase Grid Voltage | V | ×10 |
| L2 Voltage | 0x2008 | int16 | L2 Three-Phase Grid Voltage | V | ×10 |
| L3 Voltage | 0x200A | int16 | L3 Three-Phase Grid Voltage | V | ×10 |
| L1 Current | 0x200C | int16 | L1 Three-Phase Grid Output Current | A | ×1000 |
| L2 Current | 0x200E | int16 | L2 Three-Phase Grid Output Current | A | ×1000 |
| L3 Current | 0x2010 | int16 | L3 Three-Phase Grid Output Current | A | ×1000 |
| Output Power | 0x2012 | int16 | Output Power | W | ×10 |
| L1 Active Power | 0x2014 | int16 | L1 Three-Phase Grid Output Power | W | ×10 |
| L2 Active Power | 0x2016 | int16 | L2 Three-Phase Grid Output Power | W | ×10 |
| L3 Active Power | 0x2018 | int16 | L3 Three-Phase Grid Output Power | W | ×10 |
| Energy Consumed (Main) | 0x401E | int16 | Energy Consumed | kWh | ×0.1 |
| Energy Injected (Main) | 0x4028 | int16 | Energy Injected | kWh | ×0.1 |
| Energy Consumed (Alt) | 0x101E | int16 | Energy Consumed (Alt) | kWh | ×0.1 |
| Energy Injected (Alt) | 0x1028 | int16 | Energy Injected (Alt) | kWh | ×0.1 |

**Source**: Based on verified Huawei DTSU666 implementation from [rdu70/P1-2-DTSU666](https://github.com/rdu70/P1-2-DTSU666).

## Troubleshooting

### Server Not Starting
- Check if the configured port is already in use
- Ensure Home Assistant has permission to bind to the port
- Check the Home Assistant logs for error messages

### Entity Values Not Updating
- Verify the configured entities exist and have numeric values
- Check entity states are not "unknown" or "unavailable"
- Monitor the integration logs for mapping errors

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License.

## Disclaimer

This integration is for testing and development purposes. It emulates a DTSU666-H power meter but is not affiliated with or endorsed by Huawei Technologies Co., Ltd.