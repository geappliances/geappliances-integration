"""GE Appliances MQTT client."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any, cast

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .event import Event

_LOGGER = logging.getLogger()

ERD_WRITE_TOPIC = "geappliances/{}/erd/{}/write"


@dataclass
class GeaMQTTMessage:
    """Message received from MQTT integration."""

    device: str
    erd: str
    payload: bytes


class GeaMQTTClient:
    """Class to publish ERDs."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize client."""
        self._hass = hass
        self._event = Event()

    async def publish_erd(self, device_name: str, erd: int, value: bytes) -> bool:
        """Publish an ERD and return true if successful."""
        try:
            await mqtt.client.async_publish(
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
        split_topic = msg.topic.split("/")

        if await self.should_log_bad_topic(split_topic):
            _LOGGER.info("Bad GE Appliances MQTT topic: %s", msg.topic)
        else:
            device_name = split_topic[1]

            if len(split_topic) == 5:
                erd = split_topic[3]
                await self._event.publish(
                    GeaMQTTMessage(
                        device_name, erd, bytes.fromhex(cast(str, msg.payload))
                    )
                )

            else:
                await self._event.publish(
                    GeaMQTTMessage(device_name, "", bytes.fromhex(""))
                )

    async def async_subscribe(
        self, handler: Callable[[GeaMQTTMessage], Coroutine[Any, Any, None]]
    ) -> None:
        """Add function to handler list."""
        await self._event.subscribe(handler)

    async def should_log_bad_topic(self, split_topic: list[str]) -> bool:
        """Return true if the MQTT topic is bad."""
        if len(split_topic) not in [2, 3, 5]:
            return True

        if len(split_topic) == 5 and split_topic[4] not in ["write", "value"]:
            return True

        if len(split_topic) == 3 and split_topic[2] != "uptime":
            return True

        return False
