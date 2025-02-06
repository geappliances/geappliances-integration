"""Test GE Appliances binary sensor."""

import pytest
from pytest_homeassistant_custom_component.typing import MqttMockHAClient

from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from .common import (
    given_integration_is_initialized,
    given_the_appliance_api_erd_defs_are,
    given_the_appliance_api_is,
    given_the_erd_is_set_to,
    when_the_erd_is_set_to,
)

pytestmark = pytest.mark.parametrize("expected_lingering_timers", [True])

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
                            {"erd": "0x0003", "name": "Removal Test", "length": 1 }
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
                        { "erd": "0x0004", "name": "Bitfield Test", "length": 1 }
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
                    "type": "bool",
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
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                },
                {
                    "name": "Field Two",
                    "type": "bool",
                    "offset": 1,
                    "size": 1
                }
            ]
        },
        {
            "name": "Removal Test",
            "id": "0x0003",
            "operations": ["read"],
            "data": [
                {
                    "name": "Removal Test",
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Bitfield Test",
            "id": "0x0004",
            "operations": ["read"],
            "data": [
                {
                    "name": "Bit One",
                    "type": "bool",
                    "bits": {
                        "offset": 0,
                        "size": 1
                    },
                    "offset": 0,
                    "size": 1
                },
                {
                    "name": "Bit Two",
                    "type": "u8",
                    "bits": {
                        "offset": 1,
                        "size": 1
                    },
                    "offset": 0,
                    "size": 1
                },
                {
                    "name": "Reserved",
                    "type": "u8",
                    "bits": {
                        "offset": 2,
                        "size": 6
                    },
                    "offset": 0,
                    "size": 1
                }
            ]
        }
    ]
}"""


@pytest.fixture(autouse=True)
async def initialize(hass: HomeAssistant, mqtt_mock: MqttMockHAClient) -> None:
    """Set up for all tests."""
    await given_integration_is_initialized(hass, mqtt_mock)
    given_the_appliance_api_is(APPLIANCE_API_JSON, hass)
    given_the_appliance_api_erd_defs_are(APPLIANCE_API_DEFINTION_JSON, hass)
    await given_the_erd_is_set_to(0x0092, "0000 0001 0000 0001", hass)
    await given_the_erd_is_set_to(0x0093, "0000 0001 0000 0000", hass)


def the_binary_sensor_state_should_be(
    name: str, state: str, hass: HomeAssistant
) -> None:
    """Assert the state of the binary sensor."""
    if (entity := hass.states.get(name)) is not None:
        assert entity.state == state
    else:
        pytest.fail(f"Could not find binary sensor {name}")


class TestBinarySensor:
    """Hold binary sensor tests."""

    async def test_toggles_state(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test binary sensor toggles state."""
        await when_the_erd_is_set_to(0x0001, "00", hass)
        the_binary_sensor_state_should_be("binary_sensor.test_test", STATE_OFF, hass)

        await when_the_erd_is_set_to(0x0001, "01", hass)
        the_binary_sensor_state_should_be("binary_sensor.test_test", STATE_ON, hass)

    async def test_gets_correct_byte(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test binary sensor only updates based on the associated byte."""
        await when_the_erd_is_set_to(0x0002, "0000", hass)
        the_binary_sensor_state_should_be(
            "binary_sensor.multi_field_test_field_one", STATE_OFF, hass
        )
        the_binary_sensor_state_should_be(
            "binary_sensor.multi_field_test_field_two", STATE_OFF, hass
        )

        await when_the_erd_is_set_to(0x0002, "0100", hass)
        the_binary_sensor_state_should_be(
            "binary_sensor.multi_field_test_field_one", STATE_ON, hass
        )
        the_binary_sensor_state_should_be(
            "binary_sensor.multi_field_test_field_two", STATE_OFF, hass
        )

    async def test_works_with_bitfields(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test binary sensor works with read-only bitfields."""
        await when_the_erd_is_set_to(0x0004, "80", hass)

        the_binary_sensor_state_should_be(
            "binary_sensor.bitfield_test_bit_one", STATE_ON, hass
        )
        the_binary_sensor_state_should_be(
            "binary_sensor.bitfield_test_bit_two", STATE_OFF, hass
        )

    async def test_shows_unknown_when_unsupported(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test binary sensor shows STATE_UNKNOWN when the associated ERD is no longer supported."""
        await when_the_erd_is_set_to(0x0092, "0000 0001 0000 0000", hass)
        the_binary_sensor_state_should_be(
            "binary_sensor.removal_test_removal_test", STATE_UNKNOWN, hass
        )
