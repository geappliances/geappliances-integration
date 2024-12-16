"""Config flow for GE Appliances."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle GE Appliances config flow."""

    VERSION = 1

    data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if self._async_in_progress() or self._async_current_entries():
            return self.async_abort(reason="already_configured")

        await self.async_set_unique_id(DOMAIN)
        self.data = {"type": "user"}

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm appliance configuration."""

        if user_input is not None:
            _LOGGER.debug("Starting integration")
            return self.async_create_entry(title="GE Appliances", data=self.data)

        return self.async_show_form(
            step_id="confirm",
        )
