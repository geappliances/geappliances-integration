"""Test GE Appliances sensor."""

import pytest
from pytest_homeassistant_custom_component.typing import MqttMockHAClient

from homeassistant.components.sensor.const import (
    ATTR_STATE_CLASS,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import METRIC_SYSTEM

from .common import (
    given_integration_is_initialized,
    given_the_appliance_api_erd_defs_are,
    given_the_appliance_api_is,
    given_the_erd_is_set_to,
    when_the_erd_is_set_to,
)

APPLIANCE_API_JSON = """
{
    "common": {
        "versions": {
            "1": {
                "required": [
                    { "erd": "0x0001", "name": "Test", "length": 1 }
                ],
                "features": [
                    {
                        "mask": "0x00000001",
                        "name": "Primary",
                        "required": [
                            {"erd": "0x0007", "name": "Removal Test", "length": 1 }
                        ]
                    }
                ]
            }
        }
    },
    "featureApis": {
        "0": {
            "featureType": "0",
            "versions": {
                "1": {
                    "required": [
                        { "erd": "0x0002", "name": "Multi Field Test", "length": 2 },
                        { "erd": "0x0003", "name": "Temperature Test", "length": 2 },
                        { "erd": "0x0004", "name": "Enum Test", "length": 2 },
                        { "erd": "0x0005", "name": "String Test", "length": 5 },
                        { "erd": "0x0006", "name": "Total Test", "length": 1 },
                        { "erd": "0x0008", "name": "Celsius Test", "length": 2 },
                        { "erd": "0x0009", "name": "Battery Test", "length": 1 },
                        { "erd": "0x000a", "name": "Bitfield Test", "length": 1 },
                        { "erd": "0x0010", "name": "Energy Test", "length": 1 },
                        { "erd": "0x0011", "name": "Humidity Test", "length": 1 },
                        { "erd": "0x0012", "name": "Pressure Test", "length": 1 },
                        { "erd": "0x0013", "name": "Gallons Test", "length": 1 },
                        { "erd": "0x0014", "name": "Fluid Ounces Test", "length": 1 },
                        { "erd": "0x0015", "name": "Pounds Test", "length": 1 },
                        { "erd": "0x0016", "name": "Current Test", "length": 1 },
                        { "erd": "0x0017", "name": "Seconds Test", "length": 1 },
                        { "erd": "0x0018", "name": "Minutes Test", "length": 1 },
                        { "erd": "0x0019", "name": "Hours Test", "length": 1 },
                        { "erd": "0x0020", "name": "Days Test", "length": 1 },
                        { "erd": "0x0021", "name": "Power Test", "length": 1 },
                        { "erd": "0x0022", "name": "Voltage Test", "length": 1 },
                        { "erd": "0x0023", "name": "Frequency Test", "length": 1 }
                    ],
                    "features": []
                }
            }
        }
    }
}"""

APPLIANCE_API_DEFINTION_JSON = """
{
    "erds" :[
        {
            "name": "Test",
            "id": "0x0001",
            "operations": ["read"],
            "data": [
                {
                    "name": "Test",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Multi Field Test",
            "id": "0x0002",
            "operations": ["read"],
            "data": [
                {
                    "name": "Field One",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                },
                {
                    "name": "Field Two",
                    "type": "u8",
                    "offset": 1,
                    "size": 1
                }
            ]
        },
        {
            "name": "Temperature Test",
            "id": "0x0003",
            "operations": ["read"],
            "data": [
                {
                    "name": "Temperature Test",
                    "type": "i16",
                    "offset": 0,
                    "size": 2
                }
            ]
        },
        {
            "name": "Enum Test",
            "id": "0x0004",
            "operations": ["read"],
            "data": [
                {
                    "name": "Enum Test",
                    "type": "enum",
                    "values": {
                        "0": "Zero",
                        "1": "One",
                        "65535": "Max"
                    },
                    "offset": 0,
                    "size": 2
                }
            ]
        },
        {
            "name": "String Test",
            "id": "0x0005",
            "operations": ["read"],
            "data": [
                {
                    "name": "String Test",
                    "type": "string",
                    "offset": 0,
                    "size": 5
                }
            ]
        },
        {
            "name": "Total Test",
            "id": "0x0006",
            "operations": ["read"],
            "data": [
                {
                    "name": "Total Test",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Removal Test",
            "id": "0x0007",
            "operations": ["read"],
            "data": [
                {
                    "name": "Removal Test",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Celsius Test",
            "id": "0x0008",
            "operations": ["read"],
            "data": [
                {
                    "name": "Temperature (C) Test",
                    "type": "i16",
                    "offset": 0,
                    "size": 2
                }
            ]
        },
        {
            "name": "Battery Test",
            "id": "0x0009",
            "operations": ["read"],
            "data": [
                {
                    "name": "Battery Level",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Bitfield Test",
            "id": "0x000a",
            "operations": ["read"],
            "data": [
                {
                    "name": "Field One",
                    "type": "u8",
                    "bits": {
                        "offset": 0,
                        "size": 4
                    },
                    "offset": 0,
                    "size": 1
                },
                {
                    "name": "Field Two",
                    "type": "u8",
                    "bits": {
                        "offset": 4,
                        "size": 4
                    },
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Energy Test",
            "id": "0x0010",
            "operations": ["read"],
            "data": [
                {
                    "name": "Energy (kWh)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Humidity Test",
            "id": "0x0011",
            "operations": ["read"],
            "data": [
                {
                    "name": "Humidity Test",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Pressure Test",
            "id": "0x0012",
            "operations": ["read"],
            "data": [
                {
                    "name": "Pressure (in Pa)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Gallons Test",
            "id": "0x0013",
            "operations": ["read"],
            "data": [
                {
                    "name": "gallons Test",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Fluid Ounces Test",
            "id": "0x0014",
            "operations": ["read"],
            "data": [
                {
                    "name": "Fluid Ounces (oz)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Pounds Test",
            "id": "0x0015",
            "operations": ["read"],
            "data": [
                {
                    "name": "Pounds (lbs)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Current Test",
            "id": "0x0016",
            "operations": ["read"],
            "data": [
                {
                    "name": "Current (mA)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Seconds Test",
            "id": "0x0017",
            "operations": ["read"],
            "data": [
                {
                    "name": "Duration (seconds)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Minutes Test",
            "id": "0x0018",
            "operations": ["read"],
            "data": [
                {
                    "name": "Duration (minutes)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Hours Test",
            "id": "0x0019",
            "operations": ["read"],
            "data": [
                {
                    "name": "Duration (hours)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Days Test",
            "id": "0x0020",
            "operations": ["read"],
            "data": [
                {
                    "name": "Duration (days)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Power Test",
            "id": "0x0021",
            "operations": ["read"],
            "data": [
                {
                    "name": "Power (Watts)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Voltage Test",
            "id": "0x0022",
            "operations": ["read"],
            "data": [
                {
                    "name": "Voltage Test",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Frequency Test",
            "id": "0x0023",
            "operations": ["read"],
            "data": [
                {
                    "name": "Frequency (Hz)",
                    "type": "u8",
                    "offset": 0,
                    "size": 1
                }
            ]
        }
    ]
}"""


@pytest.fixture(autouse=True)
async def initialize(
    hass: HomeAssistant, mqtt_mock: MqttMockHAClient, request: pytest.FixtureRequest
) -> None:
    """Set up for all tests."""
    if "metric" in request.keywords:
        await given_integration_is_initialized(hass, mqtt_mock, METRIC_SYSTEM)
    else:
        await given_integration_is_initialized(hass, mqtt_mock)
    given_the_appliance_api_is(APPLIANCE_API_JSON, hass)
    given_the_appliance_api_erd_defs_are(APPLIANCE_API_DEFINTION_JSON, hass)
    await given_the_erd_is_set_to(0x0092, "0000 0001 0000 0001", hass)
    await given_the_erd_is_set_to(0x0093, "0000 0001 0000 0000", hass)


def the_sensor_value_should_be(name: str, state: str, hass: HomeAssistant) -> None:
    """Assert the value of the sensor."""
    if (entity := hass.states.get(name)) is not None:
        assert entity.state == state
    else:
        pytest.fail(f"Could not find sensor {name}")


def the_sensor_state_class_should_be(
    name: str, state_class: SensorStateClass, hass: HomeAssistant
) -> None:
    """Assert the sensor state class is correct."""
    if (entity := hass.states.get(name)) is not None:
        assert entity.attributes[ATTR_STATE_CLASS] == state_class
    else:
        pytest.fail(f"Could not find sensor {name}")


class TestSensor:
    """Hold sensor tests."""

    async def test_updates_state(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor updates state."""
        await when_the_erd_is_set_to(0x0001, "00", hass)
        the_sensor_value_should_be("sensor.test_test", "0", hass)

        await when_the_erd_is_set_to(0x0001, "01", hass)
        the_sensor_value_should_be("sensor.test_test", "1", hass)

    async def test_gets_correct_byte(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor only updates based on the associated byte."""
        await when_the_erd_is_set_to(0x0002, "FF00", hass)
        the_sensor_value_should_be("sensor.multi_field_test_field_one", "255", hass)
        the_sensor_value_should_be("sensor.multi_field_test_field_two", "0", hass)

        await when_the_erd_is_set_to(0x0002, "010F", hass)
        the_sensor_value_should_be("sensor.multi_field_test_field_one", "1", hass)
        the_sensor_value_should_be("sensor.multi_field_test_field_two", "15", hass)

    async def test_temperature(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor displays temperatures correctly."""
        await when_the_erd_is_set_to(0x0003, "FF01", hass)
        the_sensor_value_should_be(
            "sensor.temperature_test_temperature_test", "-255", hass
        )

    async def test_enum(self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient) -> None:
        """Test sensor displays enums correctly."""
        await when_the_erd_is_set_to(0x0004, "0000", hass)
        the_sensor_value_should_be("sensor.enum_test_enum_test", "Zero", hass)

        await when_the_erd_is_set_to(0x0004, "0001", hass)
        the_sensor_value_should_be("sensor.enum_test_enum_test", "One", hass)

        await when_the_erd_is_set_to(0x0004, "FFFF", hass)
        the_sensor_value_should_be("sensor.enum_test_enum_test", "Max", hass)

    async def test_string(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor displays strings correctly."""
        await when_the_erd_is_set_to(0x0005, bytes("hey", encoding="utf-8").hex(), hass)
        the_sensor_value_should_be("sensor.string_test_string_test", "hey", hass)

        await when_the_erd_is_set_to(0x0005, bytes("hi", encoding="utf-8").hex(), hass)
        the_sensor_value_should_be("sensor.string_test_string_test", "hi", hass)

    async def test_total(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor displays totals correctly."""
        await when_the_erd_is_set_to(0x0006, "01", hass)
        the_sensor_value_should_be("sensor.total_test_total_test", "1", hass)
        the_sensor_state_class_should_be(
            "sensor.total_test_total_test", SensorStateClass.TOTAL, hass
        )

        await when_the_erd_is_set_to(0x0006, "01", hass)
        the_sensor_value_should_be("sensor.total_test_total_test", "1", hass)

    async def test_works_with_bitfields(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor retrieves values from bitfields correctly."""
        await when_the_erd_is_set_to(0x000A, "F0", hass)
        the_sensor_value_should_be("sensor.bitfield_test_field_one", "15", hass)
        the_sensor_value_should_be("sensor.bitfield_test_field_two", "0", hass)

        await when_the_erd_is_set_to(0x000A, "0F", hass)
        the_sensor_value_should_be("sensor.bitfield_test_field_one", "0", hass)
        the_sensor_value_should_be("sensor.bitfield_test_field_two", "15", hass)

    async def test_shows_unknown_when_unsupported(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor shows STATE_UNKNOWN when the associated ERD is no longer supported."""
        await when_the_erd_is_set_to(0x0092, "0000 0001 0000 0000", hass)
        the_sensor_value_should_be(
            "sensor.removal_test_removal_test", STATE_UNKNOWN, hass
        )


def the_device_class_should_be(
    name: str, device_class: SensorDeviceClass, hass: HomeAssistant
) -> None:
    """Assert that the device class is correct for the entity."""
    if (entity := hass.states.get(name)) is not None:
        assert entity.attributes.get("device_class") == device_class
    else:
        pytest.fail(f"Could not find sensor {name}")


def the_unit_should_be(name: str, unit: str, hass: HomeAssistant) -> None:
    """Assert that the unit of measurement is correct for the entity."""
    if (entity := hass.states.get(name)) is not None:
        assert entity.attributes.get("unit_of_measurement") == unit
    else:
        pytest.fail(f"Could not find sensor {name}")


class TestSensorDeviceClasses:
    """Hold tests for sensor device classes."""

    async def test_fahrenheit_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for Fahrenheit temperatures correctly."""
        the_device_class_should_be(
            "sensor.temperature_test_temperature_test",
            SensorDeviceClass.TEMPERATURE,
            hass,
        )
        the_unit_should_be("sensor.temperature_test_temperature_test", "°F", hass)

    @pytest.mark.metric
    async def test_celsius_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for Celsius temperatures correctly."""
        the_device_class_should_be(
            "sensor.celsius_test_temperature_c_test",
            SensorDeviceClass.TEMPERATURE,
            hass,
        )
        the_unit_should_be("sensor.celsius_test_temperature_C_test", "°C", hass)

    async def test_battery_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for battery percentage correctly."""
        the_device_class_should_be(
            "sensor.battery_test_battery_level", SensorDeviceClass.BATTERY, hass
        )
        the_unit_should_be("sensor.battery_test_battery_level", "%", hass)

    async def test_energy_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for energy usage correctly."""
        the_device_class_should_be(
            "sensor.energy_test_energy_kWh", SensorDeviceClass.ENERGY, hass
        )
        the_unit_should_be("sensor.energy_test_energy_kWh", "kWh", hass)

    async def test_humidity_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for humidity correctly."""
        the_device_class_should_be(
            "sensor.humidity_test_humidity_test", SensorDeviceClass.HUMIDITY, hass
        )
        the_unit_should_be("sensor.humidity_test_humidity_test", "%", hass)

    async def test_pressure_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for pressure correctly."""
        the_device_class_should_be(
            "sensor.pressure_test_pressure_in_pa", SensorDeviceClass.PRESSURE, hass
        )
        the_unit_should_be("sensor.pressure_test_pressure_in_pa", "Pa", hass)

    async def test_gallons_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for volume in gallons correctly."""
        the_device_class_should_be(
            "sensor.gallons_test_gallons_test", SensorDeviceClass.VOLUME_STORAGE, hass
        )
        the_unit_should_be("sensor.gallons_test_gallons_test", "gal", hass)

    async def test_fluid_ounces_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for volume in fluid ounces correctly."""
        the_device_class_should_be(
            "sensor.fluid_ounces_test_fluid_ounces_oz",
            SensorDeviceClass.VOLUME_STORAGE,
            hass,
        )
        the_unit_should_be("sensor.fluid_ounces_test_fluid_ounces_oz", "fl. oz.", hass)

    async def test_pounds_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for weight in pounds correctly."""
        the_device_class_should_be(
            "sensor.pounds_test_pounds_lbs", SensorDeviceClass.WEIGHT, hass
        )
        the_unit_should_be("sensor.pounds_test_pounds_lbs", "lbs", hass)

    async def test_current_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for current in mA correctly."""
        the_device_class_should_be(
            "sensor.current_test_current_mA", SensorDeviceClass.CURRENT, hass
        )
        the_unit_should_be("sensor.current_test_current_mA", "mA", hass)

    async def test_seconds_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for duration in seconds correctly."""
        the_device_class_should_be(
            "sensor.seconds_test_duration_seconds", SensorDeviceClass.DURATION, hass
        )
        the_unit_should_be("sensor.seconds_test_duration_seconds", "s", hass)

    async def test_minutes_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for duration in minutes correctly."""
        the_device_class_should_be(
            "sensor.minutes_test_duration_minutes", SensorDeviceClass.DURATION, hass
        )
        the_unit_should_be("sensor.minutes_test_duration_minutes", "min", hass)

    async def test_hours_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for duration in hours correctly."""
        the_device_class_should_be(
            "sensor.hours_test_duration_hours", SensorDeviceClass.DURATION, hass
        )
        the_unit_should_be("sensor.hours_test_duration_hours", "h", hass)

    async def test_days_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for duration in days correctly."""
        the_device_class_should_be(
            "sensor.days_test_duration_days", SensorDeviceClass.DURATION, hass
        )
        the_unit_should_be("sensor.days_test_duration_days", "d", hass)

    async def test_power_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for power in watts correctly."""
        the_device_class_should_be(
            "sensor.power_test_power_watts", SensorDeviceClass.POWER, hass
        )
        the_unit_should_be("sensor.power_test_power_watts", "W", hass)

    async def test_voltage_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for voltage correctly."""
        the_device_class_should_be(
            "sensor.voltage_test_voltage_test", SensorDeviceClass.VOLTAGE, hass
        )
        the_unit_should_be("sensor.voltage_test_voltage_test", "V", hass)

    async def test_frequency_class_and_unit(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test sensor sets device class and unit for frequency in Hz correctly."""
        the_device_class_should_be(
            "sensor.frequency_test_frequency_hz", SensorDeviceClass.FREQUENCY, hass
        )
        the_unit_should_be("sensor.frequency_test_frequency_hz", "Hz", hass)
