"""Test GE Appliances switch."""

import pytest

from homeassistant.components import switch
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TOGGLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant

from .common import (
    given_integration_is_initialized,
    given_the_appliance_api_erd_defs_are,
    given_the_appliance_api_is,
    the_mqtt_topic_value_should_be,
    when_the_erd_is_set_to,
)

from tests.typing import MqttMockHAClient

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
                        { "erd": "0x0002", "name": "Multi Field Test", "length": 2 }
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
            "operations": ["read", "write"],
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
            "operations": ["read", "write"],
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
            "operations": ["read", "write"],
            "data": [
                {
                    "name": "Removal Test",
                    "type": "bool",
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
    await when_the_erd_is_set_to(0x0092, "0000 0001 0000 0001", hass)
    await when_the_erd_is_set_to(0x0093, "0000 0001 0000 0000", hass)


async def when_the_switch_is_turned_on(name: str, hass: HomeAssistant) -> None:
    """Turn the switch on."""
    data = {ATTR_ENTITY_ID: name}
    await hass.services.async_call(switch.DOMAIN, SERVICE_TURN_ON, data, blocking=True)


async def when_the_switch_is_turned_off(name: str, hass: HomeAssistant) -> None:
    """Turn the switch off."""
    data = {ATTR_ENTITY_ID: name}
    await hass.services.async_call(switch.DOMAIN, SERVICE_TURN_OFF, data, blocking=True)


async def when_the_switch_is_toggled(name: str, hass: HomeAssistant) -> None:
    """Toggle the switch."""
    data = {ATTR_ENTITY_ID: name}
    await hass.services.async_call(switch.DOMAIN, SERVICE_TOGGLE, data, blocking=True)


def the_switch_state_should_be(name: str, state: str, hass: HomeAssistant) -> None:
    """Assert the state of the switch."""
    assert hass.states.get(name).state == state


class TestSwitch:
    """Hold switch tests."""

    async def test_toggles_state_when_mqtt_published(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test switch toggles state."""
        await when_the_erd_is_set_to(0x0001, "00", hass)
        the_switch_state_should_be("switch.test", STATE_OFF, hass)

        await when_the_erd_is_set_to(0x0001, "01", hass)
        the_switch_state_should_be("switch.test", STATE_ON, hass)

    async def test_turns_on(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test switch publishes to MQTT when turning on."""
        await when_the_erd_is_set_to(0x0001, "00", hass)
        the_switch_state_should_be("switch.test", STATE_OFF, hass)

        await when_the_switch_is_turned_on("switch.test", hass)
        the_mqtt_topic_value_should_be(0x0001, "01", mqtt_mock)
        the_switch_state_should_be("switch.test", STATE_ON, hass)

    async def test_turns_off(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test switch publishes to MQTT when turning off."""
        await when_the_erd_is_set_to(0x0001, "01", hass)
        the_switch_state_should_be("switch.test", STATE_ON, hass)

        await when_the_switch_is_turned_off("switch.test", hass)
        the_mqtt_topic_value_should_be(0x0001, "00", mqtt_mock)
        the_switch_state_should_be("switch.test", STATE_OFF, hass)

    async def test_toggles(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test switch publishes to MQTT when toggling."""
        await when_the_erd_is_set_to(0x0001, "00", hass)
        the_switch_state_should_be("switch.test", STATE_OFF, hass)

        await when_the_switch_is_toggled("switch.test", hass)
        the_mqtt_topic_value_should_be(0x0001, "01", mqtt_mock)
        the_switch_state_should_be("switch.test", STATE_ON, hass)

        await when_the_switch_is_toggled("switch.test", hass)
        the_mqtt_topic_value_should_be(0x0001, "00", mqtt_mock)
        the_switch_state_should_be("switch.test", STATE_OFF, hass)

    async def reads_and_write_correct_byte(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test switch only reads from and writes to its associated byte."""
        await when_the_erd_is_set_to(0x0002, "0000", hass)
        the_switch_state_should_be("switch.field_one", STATE_OFF, hass)
        the_switch_state_should_be("switch.field_two", STATE_OFF, hass)

        await when_the_erd_is_set_to(0x0002, "0100", hass)
        the_switch_state_should_be("switch.field_one", STATE_ON, hass)
        the_switch_state_should_be("switch.field_two", STATE_OFF, hass)

        await when_the_switch_is_turned_off("switch.field_one", hass)
        the_mqtt_topic_value_should_be(0x0002, "0000", mqtt_mock)
        the_switch_state_should_be("switch.field_one", STATE_OFF, hass)
        the_switch_state_should_be("switch.field_two", STATE_OFF, hass)

        await when_the_switch_is_turned_on("switch.field_two", hass)
        the_mqtt_topic_value_should_be(0x0002, "0001", mqtt_mock)
        the_switch_state_should_be("switch.field_one", STATE_OFF, hass)
        the_switch_state_should_be("switch.field_two", STATE_ON, hass)

        await when_the_switch_is_toggled("switch.field_one", hass)
        the_mqtt_topic_value_should_be(0x0002, "0101", mqtt_mock)
        the_switch_state_should_be("switch.field_one", STATE_ON, hass)
        the_switch_state_should_be("switch.field_two", STATE_ON, hass)

    async def test_shows_unknown_when_unsupported(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test switch shows STATE_UNKNOWN when the associated ERD is no longer supported."""
        await when_the_erd_is_set_to(0x0092, "0000 0001 0000 0000", hass)
        the_switch_state_should_be("switch.removal_test", STATE_UNKNOWN, hass)
