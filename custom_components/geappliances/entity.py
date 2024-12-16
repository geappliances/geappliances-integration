"""GE Appliances Entity."""


class GeaEntity:
    """Superclass for GE Appliance entities."""

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
