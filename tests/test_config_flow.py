"""Test GE Appliances configuration flow."""

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def when_the_user_starts_config_flow(
    hass: HomeAssistant,
) -> ConfigFlowResult:
    """Start user config flow and return result."""
    return await hass.config_entries.flow.async_init(
        "geappliances",
        context={"source": config_entries.SOURCE_USER},
    )


def the_confirm_form_should_be_shown(result: ConfigFlowResult) -> None:
    """Assert that the confirmation form is shown."""
    assert result is not None
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"


async def when_the_user_confirms(
    hass: HomeAssistant, result: ConfigFlowResult
) -> ConfigFlowResult:
    """Click the confirm button and return result."""
    new_result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    await hass.async_block_till_done()
    return new_result


def the_entry_should_be_created(result: ConfigFlowResult) -> None:
    """Assert that the config entry has been created."""
    assert result is not None
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["type"] == "user"


class TestConfigFlow:
    """Hold config flow tests."""

    async def test_user_setup(self, hass: HomeAssistant) -> None:
        """Test config flow initiated by the user."""
        result = await when_the_user_starts_config_flow(hass)
        the_confirm_form_should_be_shown(result)

        result = await when_the_user_confirms(hass, result)
        the_entry_should_be_created(result)
