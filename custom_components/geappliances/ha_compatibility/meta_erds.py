"""Module to manage meta ERDs."""

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..const import (
    ATTR_ALLOWABLE,
    ATTR_ENABLED,
    ATTR_MAX_VAL,
    ATTR_MIN_VAL,
    ATTR_UNIQUE_ID,
    ATTR_UNIT,
    COMMON_APPLIANCE_API_ERD,
    DOMAIN,
    FEATURE_API_ERD_HIGH_END,
    FEATURE_API_ERD_HIGH_START,
    FEATURE_API_ERD_LOW_END,
    FEATURE_API_ERD_LOW_START,
    SERVICE_ENABLE_OR_DISABLE_BASE,
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
    unique_id: str,
) -> None:
    """Set the min value for the number entity."""
    min_val = int.from_bytes(min_val_bytes)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_MIN,
        {ATTR_ENTITY_ID: entity_id, ATTR_UNIQUE_ID: unique_id, ATTR_MIN_VAL: min_val},
    )


async def set_max(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    max_val_bytes: bytes,
    entity_id: str,
    unique_id: str,
) -> None:
    """Set the max value for the number entity."""
    max_val = int.from_bytes(max_val_bytes)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_MAX,
        {ATTR_ENTITY_ID: entity_id, ATTR_UNIQUE_ID: unique_id, ATTR_MAX_VAL: max_val},
    )


async def set_unit(
    hass: HomeAssistant,
    data_source: DataSource,
    meta_erd: Erd,
    unit_selection_bytes: bytes,
    entity_id: str,
    unique_id: str,
) -> None:
    """Set the unit for the number entity."""
    unit_selection = int.from_bytes(unit_selection_bytes)
    unit = await data_source.get_erd_def(meta_erd)
    if unit is not None:
        unit = unit["data"][0]["values"][f"{unit_selection}"]
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_UNIT,
            {ATTR_ENTITY_ID: entity_id, ATTR_UNIQUE_ID: unique_id, ATTR_UNIT: unit},
        )


async def enable_or_disable(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    enabled_bytes: bytes,
    entity_id: str,
    unique_id: str,
) -> None:
    """Enable or disable the entity."""
    if entity_id:
        await hass.services.async_call(
            DOMAIN,
            f"{SERVICE_ENABLE_OR_DISABLE_BASE}_{entity_id.split(".")[0]}",
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_UNIQUE_ID: unique_id,
                ATTR_ENABLED: enabled_bytes != b"\x00",
            },
        )


async def set_allowables(
    hass: HomeAssistant,
    _data_source: DataSource,
    _meta_erd: Erd,
    allowables_bytes: bytes,
    entity_id: str,
    unique_id: str,
) -> None:
    """Set the allowable options for the select entity."""
    split = unique_id.split(".")
    option = split[1]
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_ALLOWABLES,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_UNIQUE_ID: split[0],
            ATTR_ALLOWABLE: option,
            ATTR_ENABLED: (int.from_bytes(allowables_bytes) & 0xFF) != 0,
        },
    )


class MetaErdCoordinator:
    """Class to manage meta ERDs and apply transforms."""

    def __init__(
        self,
        data_source: DataSource,
        meta_erd_json: dict[Any, Any],
        hass: HomeAssistant,
    ) -> None:
        """Create the meta ERD coordinator."""
        self._entity_registry = er.async_get(hass)
        self._hass = hass
        self._data_source = data_source
        self._create_transform_table(meta_erd_json)
        self._create_entities_to_meta_erds_dict()

    def _create_transform_table(self, meta_erd_json: dict[Any, Any]) -> None:
        """Convert meta_erd_json (from meta_erds.json) into the format expected by the coordinator."""
        self._transform_table = {}

        for feature_type, versions in meta_erd_json.items():
            ft = str(feature_type)
            self._transform_table.setdefault(ft, {})
            for version, erds in versions.items():
                v = str(version)
                self._transform_table[ft].setdefault(v, {})
                for meta_erd, fields in erds.items():
                    meta_erd_int = int(meta_erd, 16)
                    meta_erd_entry = {}
                    for meta_field, transform in fields.items():
                        meta_erd_entry[meta_field] = {
                            "fields": transform["fields"],
                            "func": globals()[transform["func"]],
                        }
                    self._transform_table[ft][v][meta_erd_int] = meta_erd_entry

    def _create_entities_to_meta_erds_dict(self) -> None:
        self._entities_to_meta_erds: dict[str, list[Erd]] = {}
        for feature_type in self._transform_table:
            for feature_version in self._transform_table[feature_type]:
                for meta_erd, row_dict in self._transform_table[feature_type][
                    feature_version
                ].items():
                    for transform_row in row_dict.values():
                        for entity_id in transform_row["fields"]:
                            if self._entities_to_meta_erds.get(entity_id) is None:
                                self._entities_to_meta_erds[entity_id] = [meta_erd]
                            elif meta_erd not in self._entities_to_meta_erds[entity_id]:
                                self._entities_to_meta_erds[entity_id].append(meta_erd)

    async def is_meta_erd(self, erd: Erd) -> bool:
        """Return true if the given ERD is a meta ERD."""
        for feature_type in self._transform_table:
            for feature_version in self._transform_table[feature_type]:
                if erd in self._transform_table[feature_type][feature_version]:
                    return True

        return False

    async def _look_for_erd_def_in_appliance_api(
        self, device_name: str, api_erd: Erd, meta_erd: Erd
    ) -> tuple[str, str] | None:
        """Check the given appliance API ERD and return a tuple containing the feature type and version if it contains the given meta ERD."""
        try:
            api_value = await self._data_source.erd_read(device_name, api_erd)
        except KeyError:
            return None
        else:
            if api_erd == 0x0092:
                feature_type = "common"
                feature_version = f"{int.from_bytes(api_value[0:4])}"
                feature_mask = int.from_bytes(api_value[4:8])
                feature_def = await self._data_source.get_common_appliance_api_version(
                    feature_version
                )
            else:
                feature_type = f"{int.from_bytes(api_value[0:2])}"
                feature_version = f"{int.from_bytes(api_value[2:4])}"
                feature_mask = int.from_bytes(api_value[4:8])
                feature_def = await self._data_source.get_feature_api_version(
                    feature_type, feature_version
                )

            if TYPE_CHECKING:
                assert feature_def is not None

            for erd_def in feature_def["required"]:
                if erd_def["erd"] == f"{meta_erd:#06x}":
                    return (feature_type, feature_version)

            for feature in feature_def["features"]:
                if int(feature["mask"], base=16) & feature_mask:
                    for erd_def in feature["required"]:
                        if erd_def["erd"] == f"{meta_erd:#06x}":
                            return (feature_type, feature_version)

            return None

    async def _get_meta_erd_feature_type_and_version(
        self, device_name: str, meta_erd: Erd
    ) -> tuple[str, str] | None:
        """Return a tuple containing the feature type and version associated with the meta ERD on this device."""
        feature_type_and_version = await self._look_for_erd_def_in_appliance_api(
            device_name, COMMON_APPLIANCE_API_ERD, meta_erd
        )
        if feature_type_and_version is not None:
            return feature_type_and_version

        for api_erd in range(FEATURE_API_ERD_LOW_START, FEATURE_API_ERD_LOW_END):
            feature_type_and_version = await self._look_for_erd_def_in_appliance_api(
                device_name, api_erd, meta_erd
            )
            if feature_type_and_version is not None:
                return feature_type_and_version

        for api_erd in range(FEATURE_API_ERD_HIGH_START, FEATURE_API_ERD_HIGH_END):
            feature_type_and_version = await self._look_for_erd_def_in_appliance_api(
                device_name, api_erd, meta_erd
            )
            if feature_type_and_version is not None:
                return feature_type_and_version

        return None

    async def apply_transforms_for_meta_erd(
        self, device_name: str, meta_erd: Erd
    ) -> None:
        """Apply transforms for the given meta ERD. Will raise KeyError if meta_erd is not a meta ERD."""
        feature_type_and_version = await self._get_meta_erd_feature_type_and_version(
            device_name, meta_erd
        )
        if feature_type_and_version is None:
            return

        for meta_field, transform_row in self._transform_table[
            feature_type_and_version[0]
        ][feature_type_and_version[1]][meta_erd].items():
            field_bytes = await self.get_bytes_for_field(
                device_name, meta_erd, meta_field
            )
            if field_bytes is not None:
                for target_entity in transform_row["fields"]:
                    erd_str = target_entity.split("_", 2)[1]
                    select_option_removed = target_entity.split(".")[0]

                    await transform_row["func"](
                        self._hass,
                        self._data_source,
                        meta_erd,
                        field_bytes,
                        await self._data_source.get_entity_id_for_unique_id(
                            device_name,
                            int(erd_str, base=16),
                            select_option_removed.format(device_name),
                            target_entity.format(device_name),
                        ),
                        target_entity.format(device_name),
                    )

    async def apply_transforms_to_entity(
        self, device_name: str, entity_id: str
    ) -> None:
        """Check if any meta ERDs have transforms for the given entity and apply them."""
        meta_erds = self._entities_to_meta_erds.get(entity_id)

        if meta_erds is not None:
            for meta_erd in meta_erds:
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
                "Could not find ERD definition for meta ERD %s", f"{erd:#06x}"
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
                field_bytes = await self._get_bits_from_bytes(field_def, field_bytes)

        return field_bytes

    async def _get_bits_from_bytes(self, field_def: dict, field_bytes: bytes) -> bytes:
        """Return the bits from the bitfield for the specified ERD field."""
        offset = field_def["bits"]["offset"]
        size = field_def["bits"]["size"]

        mask = (1 << size) - 1 # Mask for the lowest `size` bytes
        mask = mask << offset # Move mask to match offset
        masked = (int.from_bytes(field_bytes) & mask) >> offset

        return masked.to_bytes()
