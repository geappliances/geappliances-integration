"""Support for GE Appliances events."""

from collections.abc import Awaitable, Callable
from typing import Any


class Event:
    """Class to represent an event."""

    def __init__(self) -> None:
        """Initialize event."""
        self._callbacks: set[Callable[[Any], Awaitable[None]]] = set()

    async def subscribe(self, callback: Callable[[Any], Awaitable[None]]) -> None:
        """Add the function to the callback set."""
        self._callbacks.add(callback)

    async def unsubscribe(self, callback: Callable[[Any], Awaitable[None]]) -> None:
        """Remove the function from the callback set."""
        self._callbacks.remove(callback)

    async def publish(self, value: Any) -> None:
        """Call all callbacks in the set with the provided value."""
        for callback in self._callbacks:
            await callback(value)

    async def has_subscribers(self) -> bool:
        """Return true if the callback set is not empty."""
        return len(self._callbacks) != 0

    async def get_subscriber_with_offset(self, offset: int) -> str | None:
        """Return the subscriber with the given field offset, if it exists."""
        for callback in self._callbacks:
            entity = callback.__self__  # type:ignore [attr-defined]
            if entity.offset == offset:
                return entity.entity_id

        return None
