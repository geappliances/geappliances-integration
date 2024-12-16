"""Constants for the GE Appliances integration."""

from homeassistant.const import Platform

type Erd = int

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

DOMAIN = "geappliances"
GEA_ENTITY_NEW = "gea_entity_new_{}"
DISCOVERY = "discovery"
APPLIANCE_API = "appliance_api"
APPLIANCE_API_DEFINITIONS = "appliance_api_definitions"

# Configuration fields
CONF_NAME = "name"
CONF_DEVICE_ID = "id"
CONF_DEVICE_MANUFACTURER = "manufacturer"
CONF_DEVICE_SERIAL_NUMBER = "serial_number"
CONF_COMMAND_TOPIC = "command_topic"
CONF_COMMAND_TEMPLATE = "command_template"
CONF_STATE_TOPIC = "state_topic"
CONF_VALUE_TEMPLATE = "value_template"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_PLATFORM = "platform"
CONF_DEVICE_CLASS = "device_class"
CONF_MIN = "min"
CONF_MAX = "max"
CONF_MODE = "mode"

# MQTT constants
SUBSCRIBE_TOPIC = "geappliances/#"

# MQTT Payload fields
DEVICE_IDENTIFIER = "identifier"
DEVICE_NAME = "name"
DEVICE_MANUFACTURER = "manufacturer"
DEVICE_SW_VERSION = "sw_version"
DEVICE_MODEL = "model"
DEVICE_SERIAL_NUMBER = "serial_number"

ERD_NAME = "name"
ERD_PLATFORM = "platform"
ERD_COMMAND_TOPIC = "command_topic"
ERD_COMMAND_TEMPLATE = "command_template"
ERD_STATE_TOPIC = "state_topic"
ERD_VALUE_TEMPLATE = "value_template"
ERD_UNIT_OF_MEASUREMENT = "unit_of_measurement"
ERD_DEVICE_CLASS = "device_class"
ERD_MIN = "min"
ERD_MAX = "max"
ERD_MODE = "mode"
