"""GE Appliances configuration factory."""

import re
from typing import Any

from homeassistant.const import Platform

from .binary_sensor import GeaBinarySensor
from .const import CONF_DEVICE_ID, CONF_NAME, Erd
from .ha_compatibility.data_source import DataSource
from .models import (
    GeaBinarySensorConfig,
    GeaEntityConfig,
    GeaNumberConfig,
    GeaSelectConfig,
    GeaSensorConfig,
    GeaSwitchConfig,
    GeaTextConfig,
)
from .number import GeaNumber, NumberConfigAttributes
from .select import GeaSelect, SelectConfigAttributes
from .sensor import GeaSensor, SensorConfigAttributes
from .switch import GeaSwitch
from .text import GeaText

PLATFORM_TYPE_LIST: list = [
    GeaBinarySensor,
    GeaNumber,
    GeaSelect,
    GeaSensor,
    GeaSwitch,
    GeaText,
]


class ConfigFactory:
    """Class to create configurations."""

    def __init__(self, data_source: DataSource) -> None:
        """Initialize factory."""
        self._data_source = data_source
        self._units_mapping: dict[str, str] = {
            r"Temperature.*\(C\)": "°C",
            r"Temperature|Fahrenheit": "°F",
            r"Battery Level": "%",
            r"kWh": "kWh",
            r"Humidity": "%",
            r"(in Pa)": "Pa",
            r"gallons": "gal",
            r"(oz)": "fl. oz.",
            r"(mL)": "mL",
            r"(L)": "L",
            r" lbs|(lbs)": "lbs",
            r"mA$| mA |(mA)": "mA",
            r"seconds": "s",
            r"minutes": "min",
            r"hours": "h",
            r"days": "d",
            r"Watts": "W",
            r"Voltage": "V",
            r"Hz": "Hz",
        }

    async def get_units(self, field: dict[str, Any]) -> str | None:
        """Determine the appropriate unit of measurement for the given field."""
        if field["type"] == "string" or field["type"] == "enum":
            return None

        for name_substring, unit in self._units_mapping.items():
            if re.search(name_substring, field["name"]) is not None:
                return unit

        return None

    async def build_binary_sensor(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> GeaBinarySensorConfig:
        """Return a binary sensor config."""
        return GeaBinarySensorConfig(
            f"{device_name}_{erd:04x}_{field[CONF_NAME]}",
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            field[CONF_NAME],
            Platform.BINARY_SENSOR,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
        )

    async def build_number(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> GeaNumberConfig:
        """Return a number config."""
        device_class = await NumberConfigAttributes.get_device_class(field)
        return GeaNumberConfig(
            f"{device_name}_{erd:04x}_{field[CONF_NAME]}",
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            field[CONF_NAME],
            Platform.NUMBER,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
            device_class,
            await self.get_units(field),
            await NumberConfigAttributes.get_min(field),
            await NumberConfigAttributes.get_max(field),
            await NumberConfigAttributes.get_value_function(field),
        )

    async def build_select(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> GeaSelectConfig:
        """Return a binary sensor config."""
        return GeaSelectConfig(
            f"{device_name}_{erd:04x}_{field[CONF_NAME]}",
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            field[CONF_NAME],
            Platform.SELECT,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
            await SelectConfigAttributes.get_enum_values(field),
        )

    async def build_sensor(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> GeaSensorConfig:
        """Return a sensor config."""
        device_class = await SensorConfigAttributes.get_device_class(field)
        return GeaSensorConfig(
            f"{device_name}_{erd:04x}_{field[CONF_NAME]}",
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            field[CONF_NAME],
            Platform.SENSOR,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
            device_class,
            await SensorConfigAttributes.get_state_class(field),
            await self.get_units(field),
            await SensorConfigAttributes.get_value_function(field),
            await SensorConfigAttributes.get_enum_values(field),
        )

    async def build_switch(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> GeaSwitchConfig:
        """Return a switch config."""
        return GeaSwitchConfig(
            f"{device_name}_{erd:04x}_{field[CONF_NAME]}",
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            field[CONF_NAME],
            Platform.SWITCH,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
        )

    async def build_text(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> GeaTextConfig:
        """Return a text config."""
        return GeaTextConfig(
            f"{device_name}_{erd:04x}_{field[CONF_NAME]}",
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            field[CONF_NAME],
            Platform.TEXT,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
        )

    async def build_config(
        self,
        device_name: str,
        erd: Erd,
        field: dict[str, Any],
        readable: bool,
        writeable: bool,
    ) -> GeaEntityConfig:
        """Build the given type of configuration."""
        platform = None
        for platform_type in PLATFORM_TYPE_LIST:
            if await platform_type.is_correct_platform_for_field(
                field, readable, writeable
            ):
                platform = platform_type
                break

        if platform == GeaBinarySensor:
            return await self.build_binary_sensor(device_name, erd, field)

        if platform == GeaNumber:
            return await self.build_number(device_name, erd, field)

        if platform == GeaSelect:
            return await self.build_select(device_name, erd, field)

        if platform == GeaSensor:
            return await self.build_sensor(device_name, erd, field)

        if platform == GeaSwitch:
            return await self.build_switch(device_name, erd, field)

        if platform == GeaText:
            return await self.build_text(device_name, erd, field)

        # Explode if we don't support the given field
        raise NotImplementedError
