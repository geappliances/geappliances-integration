"""Common values and helpers for tests."""

import json

from homeassistant.components.geappliances.const import DISCOVERY, DOMAIN, Erd
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from tests.common import MockConfigEntry, async_fire_mqtt_message
from tests.typing import MqttMockHAClient

ERD_VALUE_TOPIC = "geappliances/test/erd/{}/value"
ERD_WRITE_TOPIC = "geappliances/test/erd/{}/write"


def config_entry_stub() -> ConfigEntry:
    """Config entry version 1 fixture."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id="test",
        data={
            "name": "test",
        },
        version=1,
    )


async def given_integration_is_initialized(
    hass: HomeAssistant,
    mqtt_mock: MqttMockHAClient,
    unit_system: str = US_CUSTOMARY_SYSTEM,
) -> None:
    """Test integration sets up discovery singleton."""
    entry = config_entry_stub()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    hass.config.units = unit_system


def given_the_appliance_api_is(appliance_api: str, hass: HomeAssistant) -> None:
    """Set the appliance API for the integration."""
    hass.data[DOMAIN][DISCOVERY]._data_source._appliance_api = json.loads(appliance_api)


def given_the_appliance_api_erd_defs_are(erd_defs: str, hass: HomeAssistant) -> None:
    """Set the appliance API ERDs definitions for the integration."""
    hass.data[DOMAIN][
        DISCOVERY
    ]._data_source._appliance_api_erd_definitions = json.loads(erd_defs)["erds"]


async def given_the_erd_is_set_to(erd: Erd, state: str, hass: HomeAssistant) -> None:
    """Fire MQTT message."""
    async_fire_mqtt_message(hass, ERD_VALUE_TOPIC.format(f"{erd:#06x}"), state)
    await hass.async_block_till_done()


async def when_the_erd_is_set_to(erd: Erd, state: str, hass: HomeAssistant) -> None:
    """Fire MQTT message."""
    await given_the_erd_is_set_to(erd, state, hass)


def the_mqtt_topic_value_should_be(
    erd: Erd, state: str, mqtt_mock: MqttMockHAClient
) -> None:
    """Check the ERD was published to MQTT."""
    mqtt_mock.async_publish.assert_called_with(
        ERD_WRITE_TOPIC.format(f"{erd:#06x}"), state.lower(), 0, False
    )
