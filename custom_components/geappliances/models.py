"""Models to represent GE Appliances configurations from MQTT."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass

from .const import Erd
from .ha_compatibility.data_source import DataSource


@dataclass
class GeaEntityConfig:
    """Dataclass for holding configuration info for an entity."""

    unique_identifier: str
    device_id: str
    device_name: str
    name: str
    platform: str
    data_source: DataSource
    erd: Erd
    offset: int
    size: int


@dataclass
class GeaBinarySensorConfig(GeaEntityConfig):
    """Dataclass for holding configuration info for a binary sensor."""


@dataclass
class GeaNumberConfig(GeaEntityConfig):
    """Dataclass for holding configuration info for a number."""

    device_class: NumberDeviceClass | None
    unit: str | None
    min: float
    max: float
    value_func: Callable


@dataclass
class GeaSelectConfig(GeaEntityConfig):
    """Dataclass for holding configuration info for a select."""

    enum_vals: dict[int, str]


@dataclass
class GeaSensorConfig(GeaEntityConfig):
    """Dataclass for holding configuration info for a sensor."""

    device_class: SensorDeviceClass | None
    state_class: SensorStateClass | None
    unit: str | None
    value_func: Callable
    enum_vals: dict[int, str] | None


@dataclass
class GeaSwitchConfig(GeaEntityConfig):
    """Dataclass for holding configuration info for a switch."""


@dataclass
class GeaTextConfig(GeaEntityConfig):
    """Dataclass for holding configuration info for a text input."""
