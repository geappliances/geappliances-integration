"""The GE Appliances integration."""

from __future__ import annotations

import json
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
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not ok:
        return False

    hass.data.pop(DOMAIN)

    return True


async def get_appliance_api_json() -> str:
    """Read the appliance API JSON file and return its contents."""
    async with aiofiles.open(
        "custom_components/geappliances/appliance_api/appliance_api.json",
        encoding="utf-8",
    ) as appliance_api:
        return await appliance_api.read()


async def get_appliance_api_erd_defs_json() -> str:
    """Read the appliance API ERD definitions JSON file and return its contents."""
    async with aiofiles.open(
        "custom_components/geappliances/appliance_api/appliance_api_erd_definitions.json",
        encoding="utf-8",
    ) as appliance_api_erd_definitions:
        return await appliance_api_erd_definitions.read()


async def get_meta_erds_json() -> str:
    """Read the meta ERD JSON file and return its contents."""
    async with aiofiles.open(
        "custom_components/geappliances/meta_erds.json",
    ) as meta_erd_json_file:
        return await meta_erd_json_file.read()


async def start_discovery(hass: HomeAssistant, entry: ConfigEntry) -> GeaDiscovery:
    """Create the discovery singleton asynchronously."""

    mqtt_client = GeaMQTTClient(hass)

    data_source = DataSource(
        await get_appliance_api_json(),
        await get_appliance_api_erd_defs_json(),
        mqtt_client,
    )

    meta_erd_coordinator = MetaErdCoordinator(
        data_source, json.loads(await get_meta_erds_json()), hass
    )
    registry_updater = RegistryUpdater(hass, entry)

    gea_discovery = GeaDiscovery(registry_updater, data_source, meta_erd_coordinator)

    await mqtt.client.async_subscribe(
        hass,
        SUBSCRIBE_TOPIC,
        mqtt_client.handle_message,
    )
    await mqtt_client.async_subscribe(gea_discovery.handle_message)

    return gea_discovery
