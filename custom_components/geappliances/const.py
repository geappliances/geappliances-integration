"""Constants for the GE Appliances integration."""

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID, Platform
import homeassistant.helpers.config_validation as cv

type Erd = int

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.TIME,
]

DOMAIN = "geappliances"
GEA_ENTITY_NEW = "gea_entity_new_{}"
DISCOVERY = "discovery"
APPLIANCE_API = "appliance_api"
APPLIANCE_API_DEFINITIONS = "appliance_api_definitions"

# Configuration fields
CONF_NAME = "name"
CONF_DEVICE_ID = "id"


# MQTT constants
SUBSCRIBE_TOPIC = "geappliances/#"

# Services to update entitie attributes
ATTR_MIN_VAL = "min_val"
SERVICE_SET_MIN = "set_min"
SERVICE_SET_MIN_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_MIN_VAL): vol.Coerce(float),
    }
)

ATTR_MAX_VAL = "max_val"
SERVICE_SET_MAX = "set_max"
SERVICE_SET_MAX_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_MAX_VAL): vol.Coerce(float),
    }
)

ATTR_UNIT = "unit"
SERVICE_SET_UNIT = "set_units"
SERVICE_SET_UNIT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_UNIT): vol.Coerce(str),
    }
)

SERVICE_ENABLE_OR_DISABLE = "disable"
ATTR_ENABLED = "enabled"
SERVICE_ENABLE_OR_DISABLE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_ENABLED): vol.Coerce(bool),
    }
)

ATTR_ALLOWABLE = "allowable"
SERVICE_SET_ALLOWABLES = "set_allowables"
SERVICE_SET_ALLOWABLES_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_ALLOWABLE): vol.Coerce(str),
        vol.Required(ATTR_ENABLED): vol.Coerce(bool),
    }
)
