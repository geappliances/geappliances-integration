"""Class to set up ERDs in memory and create entities for them."""

import logging
from typing import Any

from .config_factory import ConfigFactory
from .const import Erd
from .ha_compatibility.data_source import DataSource
from .ha_compatibility.registry_updater import RegistryUpdater
from .models import GeaEntityConfig

_LOGGER = logging.getLogger(__name__)


class ERDFactory:
    """Class to set up ERDs as they are discovered."""

    def __init__(
        self, registry_updater: RegistryUpdater, data_source: DataSource
    ) -> None:
        """Store references to registry updater and data source."""
        self._registry_updater = registry_updater
        self._data_source = data_source
        self._config_factory = ConfigFactory(data_source)

    async def get_entity_configs(
        self, erd: Erd, device_name: str
    ) -> list[GeaEntityConfig]:
        """Generate an entity configuration based on the ERD and appliance type."""
        config_list = []
        if (erd_def := await self._data_source.get_erd_def(erd)) is not None:
            config_list = [
                await self._config_factory.build_config(
                    device_name,
                    erd,
                    field,
                    "read" in erd_def["operations"],
                    "write" in erd_def["operations"],
                )
                for field in erd_def["data"]
            ]
        else:
            _LOGGER.error("Could not find ERD %s", f"{erd:#06x}")

        return config_list

    async def set_up_erds(
        self, erd_api_list: list[dict[str, Any]], device_name: str
    ) -> None:
        """Set up all ERDs in the list so entities know how to interact with them."""
        for erd in erd_api_list:
            erd_int = int(erd["erd"], base=16)
            await self._data_source.add_supported_erd_to_device(
                device_name, erd_int, None
            )
            if not await self._data_source.erd_has_subscribers(device_name, erd_int):
                entity_configs = await self.get_entity_configs(erd_int, device_name)
                for config in entity_configs:
                    await self._registry_updater.add_entity_to_device(
                        config, device_name
                    )
