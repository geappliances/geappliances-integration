"""Test doubles/mocks for the GE Appliances compatibility layer."""

from unittest.mock import MagicMock

type RegistryUpdaterMock = MagicMock
type MqttClientMock = MagicMock


class AnyConfigWithName:
    """Class to match any GeaConfig object with the specified name."""

    def __init__(self, name: str) -> None:
        """Initialize."""
        self.name = name

    def __eq__(self, other) -> bool:
        """Return true if names match."""
        return self.name == other.name
