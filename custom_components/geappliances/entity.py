"""GE Appliances Entity."""

from .const import Erd
from .ha_compatibility.data_source import DataSource


class GeaEntity:
    """Superclass for GE Appliance entities."""

    _erd: Erd
    _data_source: DataSource
    _device_name: str
    _offset: int
    _size: int

    async def get_field_bytes(self, value: bytes) -> bytes:
        """Return the bytes slice associated with this entity's field."""
        return value[self._offset : (self._offset + self._size)]

    async def set_field_bytes(self, value: bytes, set_bytes: bytes) -> bytes:
        """Set the bytes associated with this entity's field and return the new value."""
        assert len(set_bytes) == self._size
        return (
            value[0 : self._offset] + set_bytes + value[(self._offset + self._size) :]
        )

    async def enable_or_disable(self, enabled: bool) -> None:
        """Enable or disable the entity."""
        if enabled:
            await self._data_source.move_erd_to_supported(self._device_name, self._erd)
        else:
            await self._data_source.move_erd_to_unsupported(
                self._device_name, self._erd
            )
