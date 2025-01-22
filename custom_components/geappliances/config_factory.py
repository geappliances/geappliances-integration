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
    GeaTimeConfig,
)
from .number import GeaNumber, NumberConfigAttributes
from .select import GeaSelect, SelectConfigAttributes
from .sensor import GeaSensor, SensorConfigAttributes
from .switch import GeaSwitch
from .text import GeaText
from .time import GeaTime

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

    async def get_unique_id(
        self, device_name: str, erd: Erd, field: dict[str, Any]
    ) -> str:
        """Generate the unique ID string for the given ERD field."""
        return f"{device_name}_{erd:04x}_{field[CONF_NAME]}".replace(" ", "_")

    async def build_base_config(
        self,
        device_name: str,
        erd: Erd,
        erd_name: str,
        field: dict[str, Any],
        platform: str,
    ) -> GeaEntityConfig:
        """Return a GeaEntity config."""
        return GeaEntityConfig(
            await self.get_unique_id(device_name, erd, field),
            (await self._data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            erd_name + ": " + field[CONF_NAME],
            platform,
            self._data_source,
            erd,
            field["offset"],
            field["size"],
        )

    async def build_binary_sensor(
        self,
        device_name: str,
        erd: Erd,
        erd_name: str,
        field: dict[str, Any],
        bit_mask=0xFF,
    ) -> GeaBinarySensorConfig:
        """Return a binary sensor config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.BINARY_SENSOR
        )

        return GeaBinarySensorConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
            bit_mask,
        )

    async def build_number(
        self,
        device_name: str,
        erd: Erd,
        erd_name: str,
        field: dict[str, Any],
        bit_mask=None,
        bit_size=0,
        bit_offset=0,
    ) -> GeaNumberConfig:
        """Return a number config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.NUMBER
        )
        device_class = await NumberConfigAttributes.get_device_class(field)

        return GeaNumberConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
            device_class,
            await self.get_units(field),
            await NumberConfigAttributes.get_min(field),
            await NumberConfigAttributes.get_max(field),
            await NumberConfigAttributes.get_value_function(field),
            bit_mask,
            bit_size,
            bit_offset,
        )

    async def build_select(
        self, device_name: str, erd: Erd, erd_name: str, field: dict[str, Any]
    ) -> GeaSelectConfig:
        """Return a select config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.SELECT
        )

        return GeaSelectConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
            await SelectConfigAttributes.get_enum_values(field),
        )

    async def build_sensor(
        self,
        device_name: str,
        erd: Erd,
        erd_name: str,
        field: dict[str, Any],
        bit_mask=None,
        bit_size=0,
        bit_offset=0,
    ) -> GeaSensorConfig:
        """Return a sensor config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.SENSOR
        )
        device_class = await SensorConfigAttributes.get_device_class(field)

        return GeaSensorConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
            device_class,
            await SensorConfigAttributes.get_state_class(field),
            await self.get_units(field),
            await SensorConfigAttributes.get_value_function(field),
            await SensorConfigAttributes.get_enum_values(field),
            bit_mask,
            bit_size,
            bit_offset,
        )

    async def build_switch(
        self,
        device_name: str,
        erd: Erd,
        erd_name: str,
        field: dict[str, Any],
        bit_mask=0xFF,
    ) -> GeaSwitchConfig:
        """Return a switch config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.SWITCH
        )

        return GeaSwitchConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
            bit_mask,
        )

    async def build_text(
        self, device_name: str, erd: Erd, erd_name: str, field: dict[str, Any]
    ) -> GeaTextConfig:
        """Return a text config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.TEXT
        )

        return GeaTextConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
        )

    async def build_time(
        self, device_name: str, erd: Erd, erd_name: str, field: dict[str, Any]
    ) -> GeaTimeConfig:
        """Return a time config."""
        base = await self.build_base_config(
            device_name, erd, erd_name, field, Platform.TIME
        )

        return GeaTimeConfig(
            base.unique_identifier,
            base.device_id,
            base.device_name,
            base.name,
            base.platform,
            base.data_source,
            base.erd,
            base.offset,
            base.size,
            "write" not in field["operations"],
        )

    async def build_config(
        self,
        device_name: str,
        erd: Erd,
        erd_name: str,
        field: dict[str, Any],
        readable: bool,
        writeable: bool,
    ) -> GeaEntityConfig:
        """Build the given type of configuration."""
        platform = None

        if field.get("bits") is not None:
            offset = field["bits"]["offset"]
            size = field["bits"]["size"]

            mask = (1 << size) - 1  # Mask for the lowest `size` bytes
            mask = mask << ((field["size"] * 8) - offset - size)
            if size == 1:
                if writeable:
                    return await self.build_switch(
                        device_name, erd, erd_name, field, mask
                    )
                return await self.build_binary_sensor(
                    device_name, erd, erd_name, field, mask
                )

            if writeable:
                return await self.build_number(
                    device_name, erd, erd_name, field, mask, size, offset
                )
            return await self.build_sensor(
                device_name, erd, erd_name, field, mask, size, offset
            )

        for platform_type in PLATFORM_TYPE_LIST:
            if await platform_type.is_correct_platform_for_field(
                field, readable, writeable
            ):
                platform = platform_type
                break

        if platform == GeaBinarySensor:
            return await self.build_binary_sensor(device_name, erd, erd_name, field)

        if platform == GeaNumber:
            return await self.build_number(device_name, erd, erd_name, field)

        if platform == GeaSelect:
            return await self.build_select(device_name, erd, erd_name, field)

        if platform == GeaSensor:
            return await self.build_sensor(device_name, erd, erd_name, field)

        if platform == GeaSwitch:
            return await self.build_switch(device_name, erd, erd_name, field)

        if platform == GeaText:
            return await self.build_text(device_name, erd, erd_name, field)

        if platform == GeaTime:
            return await self.build_time(device_name, erd, erd_name, field)

        # Explode if we don't support the given field
        raise NotImplementedError
