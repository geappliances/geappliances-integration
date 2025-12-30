"""GE Appliances MQTT device discovery."""

import logging

from .const import (
    COMMON_APPLIANCE_API_ERD,
    FEATURE_API_ERD_HIGH_END,
    FEATURE_API_ERD_HIGH_START,
    FEATURE_API_ERD_LOW_END,
    FEATURE_API_ERD_LOW_START,
    Erd,
)
from .erd_factory import ERDFactory
from .ha_compatibility.data_source import DataSource
from .ha_compatibility.meta_erds import MetaErdCoordinator
from .ha_compatibility.mqtt_client import GeaMQTTMessage
from .ha_compatibility.registry_updater import RegistryUpdater

_LOGGER = logging.getLogger(__name__)


class GeaDiscovery:
    """Class for setting up GE Appliances using MQTT discovery."""

    def __init__(
        self,
        registry_updater: RegistryUpdater,
        data_source: DataSource,
        meta_erd_coordinator: MetaErdCoordinator,
    ) -> None:
        """Initialize discovery class."""
        self._registry_updater = registry_updater
        self._erd_factory = ERDFactory(
            registry_updater, data_source, meta_erd_coordinator
        )
        self._data_source = data_source
        self._meta_erd_coordinator = meta_erd_coordinator

    async def handle_message(self, msg: GeaMQTTMessage) -> None:
        """Handle an MQTT message."""
        await self.add_device_if_not_already_exists(msg.device)

        if msg.erd != "":
            erd: Erd = int(msg.erd, base=16)
            if not await self._data_source.erd_is_supported_by_device(msg.device, erd):
                if erd == COMMON_APPLIANCE_API_ERD:
                    await self._data_source.add_unsupported_erd_to_device(
                        msg.device, erd, msg.payload
                    )
                    await self.process_common_appliance_api(msg.device, msg.payload)

                elif (FEATURE_API_ERD_LOW_START <= erd <= FEATURE_API_ERD_LOW_END) or (
                    FEATURE_API_ERD_HIGH_START <= erd <= FEATURE_API_ERD_HIGH_END
                ):
                    await self._data_source.add_unsupported_erd_to_device(
                        msg.device, erd, msg.payload
                    )
                    await self.process_feature_appliance_api(msg.device, msg.payload)

                else:
                    await self._data_source.add_unsupported_erd_to_device(
                        msg.device, erd, None
                    )

            else:
                await self._data_source.erd_write(msg.device, erd, msg.payload)
                if await self._meta_erd_coordinator.is_meta_erd(erd):
                    await self._meta_erd_coordinator.apply_transforms_for_meta_erd(
                        msg.device, erd
                    )

    async def process_common_appliance_api(self, device_name: str, data: bytes) -> None:
        """Process common appliance API manifest."""
        version = f"{int.from_bytes(data[0:4])}"
        features = int.from_bytes(data[4:8])

        common_appliance_api = await self._data_source.get_common_appliance_api_version(
            version
        )
        if common_appliance_api is None:
            _LOGGER.error("Invalid common appliance API version: %s", version)
            return

        await self._data_source.move_all_erds_to_unsupported_for_api_erd(
            device_name, None, version
        )

        await self._erd_factory.set_up_erds(
            common_appliance_api["required"], device_name
        )

        for feature in common_appliance_api["features"]:
            if int(feature["mask"], base=16) & features:
                await self._erd_factory.set_up_erds(feature["required"], device_name)

    async def process_feature_appliance_api(
        self, device_name: str, data: bytes
    ) -> None:
        """Process feature appliance API manifest."""
        feature_type = f"{int.from_bytes(data[0:2])}"
        version = f"{int.from_bytes(data[2:4])}"
        features = int.from_bytes(data[4:8])

        feature_appliance_api = await self._data_source.get_feature_api_version(
            feature_type, version
        )
        if feature_appliance_api is None:
            _LOGGER.error(
                "Invalid feature appliance API: (type: %s version: %s)",
                feature_type,
                version,
            )
            return

        await self._data_source.move_all_erds_to_unsupported_for_api_erd(
            device_name, feature_type, version
        )

        await self._erd_factory.set_up_erds(
            feature_appliance_api["required"], device_name
        )

        for feature in feature_appliance_api["features"]:
            if int(feature["mask"], base=16) & features:
                await self._erd_factory.set_up_erds(feature["required"], device_name)

    async def add_device_if_not_already_exists(self, device_name: str) -> None:
        """Add a device if not in the registry."""
        if not await self._data_source.device_exists(device_name):
            _LOGGER.debug("Adding %s", device_name)
            device_id = await self._registry_updater.create_device(device_name)
            await self._data_source.add_device(device_name, device_id)
