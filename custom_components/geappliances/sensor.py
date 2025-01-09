"""Support for GE Appliances sensors."""

from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
import logging
import re
from typing import TYPE_CHECKING, Any

from homeassistant.components import sensor
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    GEA_ENTITY_NEW,
    SERVICE_DISABLE,
    SERVICE_DISABLE_SCHEMA,
    SERVICE_SET_TIME_FORMAT,
    SERVICE_SET_TIME_FORMAT_SCHEMA,
)
from .entity import GeaEntity
from .models import GeaSensorConfig

_LOGGER = logging.getLogger(__name__)


class SensorConfigAttributes:
    """Class with helper functions for setting sensor config fields."""

    device_class_mapping: dict[str, SensorDeviceClass] = {
        r"Temperature|Fahrenheit": SensorDeviceClass.TEMPERATURE,
        r"Battery Level": SensorDeviceClass.BATTERY,
        r"kWh": SensorDeviceClass.ENERGY,
        r"Humidity": SensorDeviceClass.HUMIDITY,
        r"(in Pa)": SensorDeviceClass.PRESSURE,
        r"gallons|(oz)": SensorDeviceClass.VOLUME_STORAGE,
        r"(mL)|(L)": SensorDeviceClass.VOLUME,
        r"lbs": SensorDeviceClass.WEIGHT,
        r"mA": SensorDeviceClass.CURRENT,
        r"days|hours|minutes|seconds": SensorDeviceClass.DURATION,
        r"Watts": SensorDeviceClass.POWER,
        r"Voltage": SensorDeviceClass.VOLTAGE,
        r"Hz": SensorDeviceClass.FREQUENCY,
    }

    @classmethod
    async def get_device_class(cls, field: dict[str, Any]) -> SensorDeviceClass | None:
        """Determine the appropriate sensor device class for the given field."""
        if field["type"] == "string":
            return None

        if field["type"] == "enum":
            return SensorDeviceClass.ENUM

        for name_substring, device_class in cls.device_class_mapping.items():
            if re.search(name_substring, field["name"]) is not None:
                return device_class

        return None

    @classmethod
    async def get_state_class(cls, field: dict[str, Any]) -> SensorStateClass | None:
        """Determine the appropriate sensor state class for the given field."""
        if field["type"] in ["u8", "u16", "u32", "u64", "i8", "i16", "i32", "i64"]:
            if any(x in field["name"] for x in ("Total", "Cumulative")):
                return SensorStateClass.TOTAL
            return SensorStateClass.MEASUREMENT

        return None

    @classmethod
    async def is_value_signed(cls, field: dict[str, Any]) -> bool:
        """Return true if the field is a signed integer and false otherwise."""
        return field["type"] in ["i8", "i16", "i32"]

    @classmethod
    async def get_enum_values(cls, field: dict[str, Any]) -> dict[int, str] | None:
        """Return possible enum values or none if field is not an enum."""
        if field["type"] != "enum":
            return None

        vals: dict[int, str] = {}
        for key, val in field["values"].items():
            vals[int(key, base=10)] = val
        return vals

    @classmethod
    async def get_value_function(cls, field: dict[str, Any]) -> Callable[[bytes], Any]:
        """Return the appropriate function to format the sensor's value."""
        if await cls.is_value_signed(field):
            return lambda value: int.from_bytes(value, signed=True)

        if field["type"] == "string":
            return lambda value: value.decode("utf-8")

        return lambda value: int.from_bytes(value)  # pylint: disable=unnecessary-lambda


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GE Appliances sensor dynamically through discovery."""
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_DISABLE,
        SERVICE_DISABLE_SCHEMA,
        "enable_or_disable",
    )

    platform.async_register_entity_service(
        SERVICE_SET_TIME_FORMAT,
        SERVICE_SET_TIME_FORMAT_SCHEMA,
        "set_time_format",
    )

    entity_registry = er.async_get(hass)

    @callback
    async def async_discover(config: GeaSensorConfig) -> None:
        """Discover and add a GE Appliances binary sensor."""
        _LOGGER.debug("Adding binary sensor with name: %s", config.name)

        nonlocal entity_registry
        entity = GeaSensor(config)
        async_add_entities([entity])

        entity_registry.async_update_entity(
            entity.entity_id, device_id=config.device_id
        )

    async_dispatcher_connect(
        hass,
        GEA_ENTITY_NEW.format(sensor.const.DOMAIN),
        async_discover,
    )


class GeaSensor(SensorEntity, GeaEntity):
    """Representation of a GE Appliances binary sensor."""

    def __init__(self, config: GeaSensorConfig) -> None:
        """Initialize the binary sensor."""
        self._attr_unique_id = config.unique_identifier
        self._attr_has_entity_name = True
        self._attr_name = config.name
        self._attr_should_poll = False
        self._attr_device_class = config.device_class
        self._attr_state_class = config.state_class
        self._field_bytes: bytes | None = None
        self._attr_native_unit_of_measurement = config.unit
        self._attr_suggested_unit_of_measurement = config.unit
        self._enum_vals = config.enum_vals
        self._erd = config.erd
        self._device_name = config.device_name
        self._data_source = config.data_source
        self._offset = config.offset
        self._size = config.size
        self._value_fn = config.value_func

    @classmethod
    async def is_correct_platform_for_field(
        cls, field: dict[str, Any], readable: bool, writeable: bool
    ) -> bool:
        """Return true if sensor is an appropriate platform for the field."""
        supported_types = [
            "u8",
            "u16",
            "u32",
            "u64",
            "i8",
            "i16",
            "i32",
            "i64",
            "enum",
            "string",
        ]
        return field["type"] in supported_types and readable and not writeable

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
            self._field_bytes = None
        else:
            self._field_bytes = await self.get_field_bytes(value)

        self.async_schedule_update_ha_state(True)

    @property
    def native_value(self) -> str | int | float | date | datetime | Decimal | None:
        """Return value of the sensor."""
        if self._field_bytes is None:
            return None

        if self._attr_device_class == SensorDeviceClass.ENUM:
            if TYPE_CHECKING:
                assert self._enum_vals is not None
            return self._enum_vals.get(self._value_fn(self._field_bytes))

        return self._value_fn(self._field_bytes)

    async def set_time_format(self, format_option: int) -> None:
        """Set the time format."""
        raise NotImplementedError
