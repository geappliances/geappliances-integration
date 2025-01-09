"""Module to manage meta ERDs."""

import logging
import math

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..const import (
    ATTR_ALLOWABLE,
    ATTR_ENABLED,
    ATTR_MAX_VAL,
    ATTR_MIN_VAL,
    ATTR_UNIT,
    DOMAIN,
    SERVICE_ENABLE_OR_DISABLE,
    SERVICE_SET_ALLOWABLES,
    SERVICE_SET_MAX,
    SERVICE_SET_MIN,
    SERVICE_SET_UNIT,
    Erd,
)
from .data_source import DataSource

_LOGGER = logging.getLogger(__name__)


async def set_min(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    min_val_bytes: bytes,
    entity_id: str,
) -> None:
    """Set the min value for the number entity."""
    min_val = int.from_bytes(min_val_bytes)
    await hass.services.async_call(
        DOMAIN, SERVICE_SET_MIN, {ATTR_ENTITY_ID: entity_id, ATTR_MIN_VAL: min_val}
    )


async def set_max(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    max_val_bytes: bytes,
    entity_id: str,
) -> None:
    """Set the max value for the number entity."""
    max_val = int.from_bytes(max_val_bytes)
    await hass.services.async_call(
        DOMAIN, SERVICE_SET_MAX, {ATTR_ENTITY_ID: entity_id, ATTR_MAX_VAL: max_val}
    )


async def set_unit(
    hass: HomeAssistant,
    data_source: DataSource,
    meta_erd: Erd,
    unit_selection_bytes: bytes,
    entity_id: str,
) -> None:
    """Set the unit for the number entity."""
    unit_selection = int.from_bytes(unit_selection_bytes)
    unit = await data_source.get_erd_def(meta_erd)
    if unit is not None:
        unit = unit["data"][0]["values"][f"{unit_selection}"]
        await hass.services.async_call(
            DOMAIN, SERVICE_SET_UNIT, {ATTR_ENTITY_ID: entity_id, ATTR_UNIT: unit}
        )


async def set_time_format(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    time_format_bytes: bytes,
    entity_id: str,
) -> None:
    """Set the time format for the sensor entity."""
    raise NotImplementedError


async def enable_or_disable(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    enabled_bytes: bytes,
    entity_id: str,
) -> None:
    """Enable or disable the entity."""
    await hass.services.async_call(
        DOMAIN,
        SERVICE_ENABLE_OR_DISABLE,
        {ATTR_ENTITY_ID: entity_id, ATTR_ENABLED: enabled_bytes != b"\x00"},
    )


async def set_allowables(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    allowables_bytes: bytes,
    id_and_option: str,
) -> None:
    """Set the allowable options for the select entity."""
    split = id_and_option.split(".")
    entity_id = f"{split[0]}.{split[1]}"
    option = split[2]
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_ALLOWABLES,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_ALLOWABLE: option,
            ATTR_ENABLED: (int.from_bytes(allowables_bytes) & 0xFF) != 0,
        },
    )


class MetaErdCoordinator:
    """Class to manage meta ERDs and apply transforms."""

    def __init__(self, data_source: DataSource, hass: HomeAssistant) -> None:
        """Create the meta ERD coordinator."""
        self._entity_registry = er.async_get(hass)
        self._hass = hass
        self._data_source = data_source
        self._transform_table = _TRANSFORM_TABLE
        self._create_entities_to_meta_erds_dict()

    def _create_entities_to_meta_erds_dict(self) -> None:
        self._entities_to_meta_erds = {
            entity_id: meta_erd
            for meta_erd, row_dict in self._transform_table.items()
            for transform_row in row_dict.values()
            for entity_id in transform_row[0]
        }

    async def is_meta_erd(self, erd: Erd) -> bool:
        """Return true if the given ERD is a meta ERD."""
        return erd in self._transform_table

    async def apply_transforms_for_meta_erd(
        self, device_name: str, meta_erd: Erd
    ) -> None:
        """Apply transforms for the given meta ERD. Will raise KeyError if meta_erd is not a meta ERD."""
        for meta_field, transform_row in self._transform_table[meta_erd].items():
            field_bytes = await self.get_bytes_for_field(
                device_name, meta_erd, meta_field
            )
            if field_bytes is not None:
                for target_entity in transform_row[0]:
                    await transform_row[1](
                        self._hass,
                        self._data_source,
                        meta_erd,
                        field_bytes,
                        target_entity,
                    )

    async def apply_transforms_to_entity(
        self, device_name: str, entity_id: str
    ) -> None:
        """Check if any meta ERDs have transforms for the given entity and apply them."""
        meta_erd = self._entities_to_meta_erds.get(entity_id)

        if meta_erd is not None:
            await self.apply_transforms_for_meta_erd(device_name, meta_erd)

    async def get_bytes_for_field(
        self, device_name: str, erd: Erd, field: str
    ) -> bytes | None:
        """Return the bytes associated with the given field."""
        try:
            erd_bytes = await self._data_source.erd_read(device_name, erd)
        except KeyError:  # If the meta ERD has not been added to the device yet, erd_read will raise a KeyError.
            return None  # This is fine because the transform will be applied when the meta ERD is added.

        if erd_bytes is None:
            return None

        erd_def = await self._data_source.get_erd_def(erd)
        if erd_def is None:
            _LOGGER.error(
                "Could not fine ERD definition for meta ERD %s", f"{erd:#06x}"
            )
            return None

        for field_item in erd_def["data"]:
            if field_item["name"] == field:
                field_def = field_item

                field_bytes = erd_bytes[
                    field_def["offset"] : field_def["offset"] + field_def["size"]
                ]

        if field_bytes is not None:
            if "bits" in field_def:
                field_bytes = await self._get_bit_from_bytes(field_def, field_bytes)

        return field_bytes

    async def _get_bit_from_bytes(self, field_def: dict, field_bytes: bytes) -> bytes:
        """Return the bit from the bitfield for the specified ERD field."""
        # Right now this only supports getting a single bit but that's all we need for
        # the "allowables" meta ERDs.
        bit_def = field_def["bits"]
        byte = field_bytes[math.floor(bit_def["offset"] / 8)]
        masked = byte & (0x80 >> bit_def["offset"])

        return masked.to_bytes()


_TRANSFORM_TABLE = {
    0x0007: {
        "Temperature Display Units": (["number.target_cooling_temperature"], set_unit)
    },
    0x4040: {
        "Available Modes.Hybrid": (["select.mode.Hybrid"], set_allowables),
        "Available Modes.Standard electric": (
            ["select.mode.Standard electric"],
            set_allowables,
        ),
        "Available Modes.E-heat": (["select.mode.E-heat"], set_allowables),
        "Available Modes.HiDemand": (["select.mode.HiDemand"], set_allowables),
        "Available Modes.Vacation": (["select.mode.Vacation"], set_allowables),
    },
    0x4047: {
        "Minimum setpoint": (["number.temperature"], set_min),
        "Maximum setpoint": (["number.temperature"], set_max),
    },
    0x214E: {
        "Eco Option Is In Client Writable State": (
            ["select.eco_option_status"],
            enable_or_disable,
        )
    },
}
