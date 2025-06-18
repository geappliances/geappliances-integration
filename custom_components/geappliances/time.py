"""Support for GE Appliances time inputs."""

from datetime import time
import logging
from typing import Any

from homeassistant.components.time import TimeEntity, const as time_const
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import entity_platform, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_ENABLED,
    ATTR_UNIQUE_ID,
    GEA_ENTITY_NEW,
    SERVICE_ENABLE_OR_DISABLE_BASE,
    SERVICE_ENABLE_OR_DISABLE_SCHEMA,
)
from .entity import GeaEntity
from .models import GeaTimeConfig

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GE Appliances time input dynamically through discovery."""
    platform = entity_platform.async_get_current_platform()
    SERVICE_ENABLE_OR_DISABLE = SERVICE_ENABLE_OR_DISABLE_BASE + "_time"

    async def handle_service_call(entity: GeaTime, service_call: ServiceCall) -> None:
        if entity.unique_id == service_call.data[ATTR_UNIQUE_ID]:
            if service_call.service == SERVICE_ENABLE_OR_DISABLE:
                await entity.enable_or_disable(service_call.data[ATTR_ENABLED])

    platform.async_register_entity_service(
        SERVICE_ENABLE_OR_DISABLE,
        SERVICE_ENABLE_OR_DISABLE_SCHEMA,
        handle_service_call,
    )

    entity_registry = er.async_get(hass)

    @callback
    async def async_discover(config: GeaTimeConfig) -> None:
        """Discover and add a GE Appliances time input."""
        _LOGGER.debug("Adding time with name: %s", config.name)

        nonlocal entity_registry
        entity = GeaTime(config)
        async_add_entities([entity])

        entity_registry.async_update_entity(
            entity.entity_id, device_id=config.device_id
        )

    async_dispatcher_connect(
        hass,
        GEA_ENTITY_NEW.format(time_const.DOMAIN),
        async_discover,
    )


class GeaTime(TimeEntity, GeaEntity):
    """Representation of a GE Appliances time input - allows the user to set values for numerical ERDs."""

    def __init__(self, config: GeaTimeConfig) -> None:
        """Initialize the time."""
        self._attr_unique_id = config.unique_identifier
        self._attr_has_entity_name = True
        self._attr_name = config.name
        self._attr_should_poll = False
        self._field_bytes: bytes | None = None
        self._erd = config.erd
        self._status_erd = config.status_erd or config.erd
        self._device_name = config.device_name
        self._data_source = config.data_source
        self._offset = config.offset
        self._size = config.size
        self._is_read_only = config.is_read_only
        self._attr_native_value = None

    @classmethod
    async def is_correct_platform_for_field(
        cls, field: dict[str, Any], writeable: bool
    ) -> bool:
        """Return true if time is an appropriate platform for the field."""
        # Right now the only ERD that should use this platform is 0x0005, which is handled
        # as a special case
        return False

    async def async_added_to_hass(self) -> None:
        """Set initial state from ERD and set up callback for updates."""
        value = await self._data_source.erd_read(self._device_name, self._status_erd)
        await self.erd_updated(value)

        await self._data_source.erd_subscribe(
            self._device_name, self._status_erd, self.erd_updated
        )
        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from the ERD."""
        await self._data_source.erd_unsubscribe(
            self._device_name, self._status_erd, self.erd_updated
        )

    @callback
    async def erd_updated(self, value: bytes | None) -> None:
        """Update state from ERD."""
        if value is None:
            self._field_bytes = None
        else:
            self._field_bytes = await self.get_field_bytes(value)

        self.async_schedule_update_ha_state(True)

    async def _get_bytes_from_value(self, value: time) -> bytes:
        """Cast the time to bytes."""
        return bytes([value.hour, value.minute, value.second])

    async def async_set_value(self, value: time) -> None:
        """Update the value."""
        if self._is_read_only:
            self.async_schedule_update_ha_state(
                True
            )  # Force update to wipe out user input
            return

        erd_value = await self._data_source.erd_read(self._device_name, self._erd)
        if erd_value is not None:
            value_bytes = await self._get_bytes_from_value(value)
            await self._data_source.erd_publish(
                self._device_name,
                self._erd,
                await self.set_field_bytes(erd_value, value_bytes),
            )

    @property
    def native_value(self) -> time | None:
        """Return value of the time."""
        if self._field_bytes is None:
            return None

        hour = int.from_bytes(self._field_bytes[0:1])
        minute = int.from_bytes(self._field_bytes[1:2])
        second = int.from_bytes(self._field_bytes[2:3])

        return time(hour, minute, second)
