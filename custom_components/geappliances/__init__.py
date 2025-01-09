"""The GE Appliances integration."""

from __future__ import annotations

import logging

import aiofiles

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DISCOVERY, DOMAIN, PLATFORMS, SUBSCRIBE_TOPIC
from .discovery import GeaDiscovery
from .ha_compatibility.data_source import DataSource
from .ha_compatibility.meta_erds import MetaErdCoordinator
from .ha_compatibility.mqtt_client import GeaMQTTClient
from .ha_compatibility.registry_updater import RegistryUpdater

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GE Appliances from a config entry."""

    if not await mqtt.util.async_wait_for_mqtt_client(hass):
        _LOGGER.error("MQTT integration is not available")
        return False

    hass.data[DOMAIN] = {}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    hass.data[DOMAIN][DISCOVERY] = await start_discovery(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data.pop(DOMAIN)
        return ok

    return False


async def start_discovery(hass: HomeAssistant, entry: ConfigEntry) -> GeaDiscovery:
    """Create the discovery singleton asynchronously."""

    mqtt_client = GeaMQTTClient(hass)

    async with aiofiles.open(
        "custom_components/geappliances/appliance_api/appliance_api.json",
        encoding="utf-8",
    ) as appliance_api:
        contents_api = await appliance_api.read()

        async with aiofiles.open(
            "custom_components/geappliances/appliance_api/appliance_api_erd_definitions.json",
            encoding="utf-8",
        ) as appliance_api_erd_definitions:
            contents_api_erd_defintions = await appliance_api_erd_definitions.read()
            data_source = DataSource(
                contents_api, contents_api_erd_defintions, mqtt_client
            )

    registry_updater = RegistryUpdater(hass, entry)
    meta_erd_coordinator = MetaErdCoordinator(data_source, hass)
    gea_discovery = GeaDiscovery(registry_updater, data_source, meta_erd_coordinator)

    await mqtt.client.async_subscribe(
        hass,
        SUBSCRIBE_TOPIC,
        mqtt_client.handle_message,
    )
    await mqtt_client.async_subscribe(gea_discovery.handle_message)

    return gea_discovery
