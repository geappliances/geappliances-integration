"""Module to manage special ERDs."""

from collections.abc import Sequence
import logging

from custom_components.geappliances.models import GeaEntityConfig, GeaTimeConfig
from homeassistant.const import Platform

from ..config_factory import ConfigFactory
from ..const import CONF_DEVICE_ID, Erd
from .data_source import DataSource

_LOGGER = logging.getLogger(__name__)


async def build_clock_time(
    device_name: str, data_source: DataSource
) -> list[GeaTimeConfig]:
    """Build the clock time entity for ERD 0x0005."""
    return [
        GeaTimeConfig(
            f"{device_name}_0005_Clock_Time",
            (await data_source.get_device(device_name))[CONF_DEVICE_ID],
            device_name,
            "Clock Time",
            Platform.TIME,
            data_source,
            0x0005,
            0,
            3,
            True,
        )
    ]


class SpecialErdCoordinator:
    """Class to manage special ERDs."""

    def __init__(
        self,
        data_source: DataSource,
        config_factory: ConfigFactory,
    ) -> None:
        """Create the special ERD coordinator."""
        self._data_source = data_source
        self._config_factory = config_factory
        self._special_erds_map = _SPECIAL_ERDS_MAP

    async def is_special_erd(self, erd: Erd) -> bool:
        """Return true if the given ERD is a special ERD."""
        return erd in self._special_erds_map

    async def build_config_for_erd(
        self, device_name: str, erd: Erd
    ) -> Sequence[GeaEntityConfig]:
        """Create the config entity for the given ERD. Raise KeyError if the ERD is not a special ERD."""
        return await self._special_erds_map[erd](device_name, self._data_source)


_SPECIAL_ERDS_MAP = {0x0005: build_clock_time}
