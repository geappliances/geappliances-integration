"""Test GE Appliances text."""

from custom_components.geappliances.const import Erd
import pytest
from pytest_homeassistant_custom_component.common import async_fire_mqtt_message
from pytest_homeassistant_custom_component.typing import MqttMockHAClient

from homeassistant.components import text
from homeassistant.components.text.const import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from .common import (
    ERD_VALUE_TOPIC,
    given_integration_is_initialized,
    given_the_appliance_api_erd_defs_are,
    given_the_appliance_api_is,
    given_the_erd_is_set_to,
    the_mqtt_topic_value_should_be,
    when_the_erd_is_set_to,
)

pytestmark = pytest.mark.parametrize("expected_lingering_timers", [True])

APPLIANCE_API_JSON = """
{
    "common": {
        "versions": {
            "1": {
                "required": [
                    { "erd": "0x0001", "name": "Test", "length": 4 }
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
                        { "erd": "0x0002", "name": "Multi Field Test", "length": 11 },
                        { "erd": "0x0004", "name": "Raw Test", "length": 6 }

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
                    "type": "string",
                    "offset": 0,
                    "size": 4
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
                    "type": "string",
                    "offset": 0,
                    "size": 5
                },
                {
                    "name": "Field Two",
                    "type": "string",
                    "offset": 5,
                    "size": 6
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
                    "type": "string",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Raw Test",
            "id": "0x0004",
            "operations": ["read", "write"],
            "data": [
                {
                    "name": "Field One",
                    "type": "raw",
                    "offset": 0,
                    "size": 4
                },
                {
                    "name": "Field Two",
                    "type": "raw",
                    "offset": 4,
                    "size": 2
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


async def given_the_erd_string_is_set_to(
    erd: Erd, text: str, hass: HomeAssistant
) -> None:
    """Fire MQTT message, encoding the text as a hex string."""
    async_fire_mqtt_message(
        hass, ERD_VALUE_TOPIC.format(f"{erd:#06x}"), text.encode().hex()
    )
    await hass.async_block_till_done()


async def when_the_erd_string_is_set_to(
    erd: Erd, text: str, hass: HomeAssistant
) -> None:
    """Fire MQTT message, encoding the text as a hex string."""
    await given_the_erd_string_is_set_to(erd, text, hass)


async def when_the_text_is_set_to(name: str, value: str, hass: HomeAssistant) -> None:
    """Set the text value."""
    data = {ATTR_ENTITY_ID: name, ATTR_VALUE: value}
    await hass.services.async_call(text.DOMAIN, SERVICE_SET_VALUE, data, blocking=True)


def the_text_value_should_be(name: str, state: str, hass: HomeAssistant) -> None:
    """Assert the value of the text input."""
    if (entity := hass.states.get(name)) is not None:
        assert entity.state == state
    else:
        pytest.fail(f"Could not find text {name}")


async def the_text_should_except_when_set_to(
    name: str, value: str, hass: HomeAssistant
) -> None:
    """Assert that attempting to set the text value raises a ValueError."""
    with pytest.raises(ValueError):
        await when_the_text_is_set_to(name, value, hass)


class TestText:
    """Hold text input tests."""

    async def test_updates_state(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test text input updates state."""
        await when_the_erd_string_is_set_to(0x0001, "hi", hass)
        the_text_value_should_be("text.test_test", "hi", hass)

        await when_the_erd_string_is_set_to(0x0001, "bye", hass)
        the_text_value_should_be("text.test_test", "bye", hass)

    async def test_gets_correct_bytes(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test text input only updates based on the associated bytes."""
        await when_the_erd_string_is_set_to(0x0002, "hello", hass)
        the_text_value_should_be("text.multi_field_test_field_one", "hello", hass)
        the_text_value_should_be("text.multi_field_test_field_two", "", hass)

        await when_the_erd_string_is_set_to(0x0002, "hello,world", hass)
        the_text_value_should_be("text.multi_field_test_field_one", "hello", hass)
        the_text_value_should_be("text.multi_field_test_field_two", ",world", hass)

    async def test_sets_correct_bytes(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test text input only updates the associated bytes."""
        await given_the_erd_string_is_set_to(0x0002, "aaa", hass)
        await when_the_text_is_set_to("text.multi_field_test_field_one", "hello", hass)
        the_mqtt_topic_value_should_be(0x0002, b"hello".hex(), mqtt_mock)
        the_text_value_should_be("text.multi_field_test_field_one", "hello", hass)
        the_text_value_should_be("text.multi_field_test_field_two", "", hass)

        await when_the_text_is_set_to("text.multi_field_test_field_two", ",world", hass)
        the_mqtt_topic_value_should_be(0x0002, b"hello,world".hex(), mqtt_mock)
        the_text_value_should_be("text.multi_field_test_field_one", "hello", hass)
        the_text_value_should_be("text.multi_field_test_field_two", ",world", hass)

    async def test_string_too_long(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test the text input raises exception when the string is too long."""
        await given_the_erd_string_is_set_to(0x0001, "hi", hass)
        await the_text_should_except_when_set_to("text.test_test", "hello1234", hass)
        the_text_value_should_be("text.test_test", "hi", hass)

    async def test_represents_raw_bytes_as_hex_strings(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test text represents raw fields as hexadecimal strings."""
        await when_the_erd_is_set_to(0x0004, "0102 0304 0506", hass)

        the_text_value_should_be("text.raw_test_field_one", "01020304", hass)
        the_text_value_should_be("text.raw_test_field_two", "0506", hass)

    async def test_validates_hex_strings_for_raw_bytes(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test text raises error when input is not a valid hex string."""
        await given_the_erd_is_set_to(0x0004, "0102 0304 0506", hass)

        await the_text_should_except_when_set_to(
            "text.raw_test_field_one", "hello", hass
        )
        the_text_value_should_be("text.raw_test_field_one", "01020304", hass)

    async def test_shows_unknown_when_unsupported(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test text shows STATE_UNKNOWN when the associated ERD is no longer supported."""
        await when_the_erd_is_set_to(0x0092, "0000 0001 0000 0000", hass)
        the_text_value_should_be("text.removal_test_removal_test", STATE_UNKNOWN, hass)
