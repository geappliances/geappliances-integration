"""Constants for the GE Appliances integration."""

import re
from typing import Any

import voluptuous as vol  # type:ignore [import-untyped]

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

COMMON_APPLIANCE_API_ERD = 0x0092
FEATURE_API_ERD_LOW_START = 0x0093
FEATURE_API_ERD_LOW_END = 0x0097
FEATURE_API_ERD_HIGH_START = 0x0109
FEATURE_API_ERD_HIGH_END = 0x010D

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

# Services to update entity attributes
VALID_UNIQUE_ID = re.compile(r".*_[a-z0-9]{4}_.*")


def unique_id(value: Any) -> str:
    """Validate Entity ID."""
    str_value = cv.string(value)
    if VALID_UNIQUE_ID.match(str_value) is not None:
        return str_value

    raise vol.Invalid(f"Unique ID {value} is an invalid unique ID")


ATTR_UNIQUE_ID = "unique_id"
SERVICE_BASE_SCHEMA = {
    vol.Required(ATTR_ENTITY_ID): vol.Any(cv.entity_id, None),
    vol.Required(ATTR_UNIQUE_ID): unique_id,
}

ATTR_MIN_VAL = "min_val"
SERVICE_SET_MIN = "set_min"
SERVICE_SET_MIN_SCHEMA = SERVICE_BASE_SCHEMA | {
    vol.Required(ATTR_MIN_VAL): vol.Coerce(float),
}


ATTR_MAX_VAL = "max_val"
SERVICE_SET_MAX = "set_max"
SERVICE_SET_MAX_SCHEMA = SERVICE_BASE_SCHEMA | {
    vol.Required(ATTR_MAX_VAL): vol.Coerce(float),
}


ATTR_UNIT = "unit"
SERVICE_SET_UNIT = "set_units"
SERVICE_SET_UNIT_SCHEMA = SERVICE_BASE_SCHEMA | {
    vol.Required(ATTR_UNIT): vol.Coerce(str),
}

SERVICE_ENABLE_OR_DISABLE = "disable"
ATTR_ENABLED = "enabled"
SERVICE_ENABLE_OR_DISABLE_SCHEMA = SERVICE_BASE_SCHEMA | {
    vol.Required(ATTR_ENABLED): vol.Coerce(bool),
}


ATTR_ALLOWABLE = "allowable"
SERVICE_SET_ALLOWABLES = "set_allowables"
SERVICE_SET_ALLOWABLES_SCHEMA = SERVICE_BASE_SCHEMA | {
    vol.Required(ATTR_ALLOWABLE): vol.Coerce(str),
    vol.Required(ATTR_ENABLED): vol.Coerce(bool),
}
