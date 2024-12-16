"""Support for GE Appliances binary sensors."""

import logging
from typing import Any

from homeassistant.components import binary_sensor
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import GEA_ENTITY_NEW
from .entity import GeaEntity
from .models import GeaBinarySensorConfig

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GE Appliances binary sensor dynamically through discovery."""
    entity_registry = er.async_get(hass)

    @callback
    async def async_discover(config: GeaBinarySensorConfig) -> None:
        """Discover and add a GE Appliances binary sensor."""
        _LOGGER.debug("Adding binary sensor with name: %s", config.name)

        nonlocal entity_registry
        entity = GeaBinarySensor(config)
        async_add_entities([entity])

        entity_registry.async_update_entity(
            entity.entity_id, device_id=config.device_id
        )

    async_dispatcher_connect(
        hass,
        GEA_ENTITY_NEW.format(binary_sensor.DOMAIN),
        async_discover,
    )


class GeaBinarySensor(BinarySensorEntity, GeaEntity):
    """Representation of a GE Appliances binary sensor."""

    def __init__(self, config: GeaBinarySensorConfig) -> None:
        """Initialize the binary sensor."""
        self._attr_unique_id = config.unique_identifier
        self._attr_has_entity_name = True
        self._attr_name = config.name
        self._attr_should_poll = False
        self._erd = config.erd
        self._device_name = config.device_name
        self._data_source = config.data_source
        self._offset = config.offset
        self._size = config.size

    @classmethod
    async def is_correct_platform_for_field(
        cls, field: dict[str, Any], readable: bool, writeable: bool
    ) -> bool:
        """Return true if binary sensor is an appropriate platform for the field."""
        return field["type"] == "bool" and readable and not writeable

    async def async_added_to_hass(self) -> None:
        """Set initial state from ERD and set up callback for updates."""
        value = await self._data_source.erd_read(self._device_name, self._erd)
        await self.erd_updated(value)

        await self._data_source.erd_subscribe(
            self._device_name, self._erd, self.erd_updated
        )
        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from the ERD."""
        await self._data_source.erd_unsubscribe(
            self._device_name, self._erd, self.erd_updated
        )

    @callback
    async def erd_updated(self, value: bytes | None) -> None:
        """Update state from ERD."""
        if value is None:
            self._attr_is_on = None
            return

        self._attr_is_on = (await self.get_field_bytes(value)) != b"\x00"

        self.async_schedule_update_ha_state(True)

    @property
    async def async_is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self._attr_is_on
