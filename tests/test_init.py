"""Test GE Appliances initialization."""

from custom_components.geappliances.const import DISCOVERY, DOMAIN
from custom_components.geappliances.discovery import GeaDiscovery
from pytest_homeassistant_custom_component.typing import MqttMockHAClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .common import config_entry_stub


def given_the_entry_is_created(hass: HomeAssistant) -> ConfigEntry:
    """Create the config entry and add it to HA."""
    entry = config_entry_stub()
    entry.add_to_hass(hass)
    return entry


async def setup_should_return(
    val: bool, hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Assert that the setup returns val."""
    assert await hass.config_entries.async_setup(entry.entry_id) is val


def discovery_should_be_created(hass: HomeAssistant) -> None:
    """Assert that the GEADiscovery singleton is created."""
    assert type(hass.data[DOMAIN][DISCOVERY]) is GeaDiscovery


class TestInit:
    """Hold initialization tests."""

    async def test_mqtt_unavailable(self, hass: HomeAssistant) -> None:
        """Test MQTT unavailable."""
        entry = given_the_entry_is_created(hass)
        await setup_should_return(False, hass, entry)

    async def test_discovery_is_setup(
        self, hass: HomeAssistant, mqtt_mock: MqttMockHAClient
    ) -> None:
        """Test integration sets up discovery singleton."""
        entry = given_the_entry_is_created(hass)
        await hass.async_block_till_done(wait_background_tasks=True)
        await setup_should_return(True, hass, entry)
        await hass.async_block_till_done(wait_background_tasks=True)
        discovery_should_be_created(hass)
        await hass.async_block_till_done(wait_background_tasks=True)
