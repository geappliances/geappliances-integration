"""GE Appliances MQTT client."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any, cast

from homeassistant.components import mqtt
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .event import Event

_LOGGER = logging.getLogger()

ERD_WRITE_TOPIC = "geappliances/{}/erd/{}/write"


@dataclass
class MQTTMessage:
    """Message received from MQTT integration."""

    topic: str
    payload: bytes
    qos: int
    retain: bool
    subscribed_topic: str
    timestamp: float


class GeaMQTTClient:
    """Class to publish ERDs."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize client."""
        self._hass = hass
        self._event = Event()

    async def publish_erd(self, device_name: str, erd: int, value: bytes) -> bool:
        """Publish an ERD and return true if successful."""
        try:
            await mqtt.async_publish(
                self._hass,
                ERD_WRITE_TOPIC.format(device_name, f"{erd:#06x}"),
                value.hex(),
                0,
                False,
            )
        except HomeAssistantError:
            _LOGGER.error("MQTT publish failed for ERD %s", f"{erd:#06x}")
            return False
        else:
            return True

    async def handle_message(self, msg: ReceiveMessage):
        """Convert MQTT message to our message type and pass it on to discovery."""
        casted_msg = MQTTMessage(
            msg.topic,
            bytes.fromhex(cast(str, msg.payload)),
            msg.qos,
            msg.retain,
            msg.subscribed_topic,
            msg.timestamp,
        )
        await self._event.publish(casted_msg)

    async def async_subscribe(
        self, handler: Callable[[MQTTMessage], Coroutine[Any, Any, None]]
    ) -> None:
        """Add function to handler list."""
        await self._event.subscribe(handler)
