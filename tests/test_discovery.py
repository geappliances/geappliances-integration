"""Test GE Appliances MQTT discovery."""

import logging
from unittest.mock import MagicMock

from custom_components.geappliances.const import Erd
from custom_components.geappliances.discovery import GeaDiscovery
from custom_components.geappliances.ha_compatibility.data_source import DataSource
from custom_components.geappliances.ha_compatibility.meta_erds import MetaErdCoordinator
from custom_components.geappliances.ha_compatibility.mqtt_client import GeaMQTTMessage
from custom_components.geappliances.ha_compatibility.registry_updater import (
    RegistryUpdater,
)
import pytest

from .common import ERD_VALUE_TOPIC
from .doubles import (
    AnyConfigWithName,
    MetaErdCoordinatorMock,
    MqttClientMock,
    RegistryUpdaterMock,
)

DEVICE_TOPIC = "geappliances/test"
APPLIANCE_API_JSON = """
{
    "common": {
        "versions": {
            "1": {
                "required": [
                    { "erd": "0x0001", "name": "Test", "length": 1 }
                ],
                "features": [
                    {
                        "mask": "0x00000001",
                        "name": "Primary",
                        "required": [
                            {"erd": "0x0002", "name": "Another Test", "length": 1 }
                        ]
                    }
                ]
            }
        }
    },
    "featureApis": {
        "0": {
            "featureType": "0",
            "versions": {
                "1": {
                    "required": [
                        { "erd": "0x0003", "name": "Feature Test", "length": 1 }
                    ],
                    "features": [
                        {
                            "mask": "0x00000001",
                            "name": "Primary",
                            "required": [
                                {"erd": "0x0004", "name": "Another Feature Test", "length": 1 }
                            ]
                        }
                    ]
                }
            }
        },
        "1": {
            "featureType": "1",
            "versions": {
                "1": {
                    "required": [
                        { "erd": "0x0005", "name": "Multi Field Test", "length": 2 }
                    ],
                    "features": []
                }
            }
        }
    }
}"""
APPLIANCE_API_DEFINTION_JSON = """
{
    "erds" :[
        {
            "name": "Test",
            "id": "0x0001",
            "operations": ["read"],
            "data": [
                {
                    "name": "Test",
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Another Test",
            "id": "0x0002",
            "operations": ["read"],
            "data": [
                {
                    "name": "Another Test",
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Feature Test",
            "id": "0x0003",
            "operations": ["read"],
            "data": [
                {
                    "name": "Feature Test",
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Another Feature Test",
            "id": "0x0004",
            "operations": ["read"],
            "data": [
                {
                    "name": "Another Feature Test",
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                }
            ]
        },
        {
            "name": "Multi Field Test",
            "id": "0x0005",
            "operations": ["read"],
            "data": [
                {
                    "name": "Field One",
                    "type": "bool",
                    "offset": 0,
                    "size": 1
                },
                {
                    "name": "Field Two",
                    "type": "bool",
                    "offset": 1,
                    "size": 1
                }
            ]
        }
    ]
}"""


@pytest.fixture
def data_source(mqtt_client_mock: MqttClientMock) -> DataSource:
    """Create a data source using the module's appliance API."""
    return DataSource(
        APPLIANCE_API_JSON, APPLIANCE_API_DEFINTION_JSON, mqtt_client_mock
    )


@pytest.fixture
def capture_errors(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    """Capture all logged errors in a test."""
    caplog.set_level(logging.ERROR)
    return caplog


@pytest.fixture
def registry_updater_mock() -> RegistryUpdaterMock:
    """Return a mock instance of RegistryUpdater."""
    return MagicMock(RegistryUpdater)


@pytest.fixture
def meta_erd_coordinator_mock() -> MetaErdCoordinatorMock:
    """Return a mock instance of MetaErdCoordinator."""
    attrs = {"is_meta_erd.return_value": False}
    meta_erd_coordinator_mock = MagicMock(MetaErdCoordinator)
    meta_erd_coordinator_mock.configure_mock(**attrs)
    return meta_erd_coordinator_mock


@pytest.fixture
def discovery(
    registry_updater_mock, data_source, meta_erd_coordinator_mock
) -> GeaDiscovery:
    """Return an instance of GeaDiscovery."""
    return GeaDiscovery(registry_updater_mock, data_source, meta_erd_coordinator_mock)


@pytest.fixture(autouse=True)
def set_special_erd_map(discovery) -> None:
    """Set the special ERD map to empty to avoid interfering with tests."""
    discovery._erd_factory._special_erd_coordinator._special_erds_map = {}


async def given_the_erd_is_set_to(
    erd: Erd,
    payload: bytes,
    discovery: GeaDiscovery,
) -> None:
    """Fake an MQTT message."""
    await discovery.handle_message(
        GeaMQTTMessage("test", "{}".format(f"{erd:#06x}"), payload)
    )


async def when_the_device_is_discovered(discovery: GeaDiscovery) -> None:
    """Fire device discovery message."""
    await discovery.handle_message(GeaMQTTMessage("test", "", b""))


async def when_the_erd_is_set_to(
    erd: Erd,
    payload: bytes,
    discovery: GeaDiscovery,
) -> None:
    """Fake an MQTT message."""
    await given_the_erd_is_set_to(erd, payload, discovery)


async def when_an_mqtt_message_is_received_on_topic(
    topic: str,
    payload: bytes,
    discovery: GeaDiscovery,
) -> None:
    """Fake an MQTT message."""
    split_topic = topic.split("/")
    device_name = split_topic[1]
    erd = split_topic[3]
    await discovery.handle_message(GeaMQTTMessage(device_name, erd, payload))


def the_device_should_exist(registry_updater_mock: RegistryUpdaterMock) -> None:
    """Check the device has been registered."""
    registry_updater_mock.create_device.assert_called_with("test")


def the_entity_should_be_added_to_the_device(
    entity_name: str, registry_updater_mock: RegistryUpdaterMock
) -> None:
    """Check the entity has been registered with the device."""
    registry_updater_mock.add_entity_to_device.assert_any_call(
        AnyConfigWithName(entity_name), "test"
    )


def the_entity_should_not_exist(
    entity_name: str, registry_updater_mock: RegistryUpdaterMock
) -> None:
    """Assert the given entity does not exist."""
    try:
        registry_updater_mock.add_entity_to_device.assert_any_call(
            AnyConfigWithName(entity_name), "test"
        )
    except AssertionError:
        return

    pytest.fail(f"Entity with name {entity_name} was found on device 'test'")


def the_erd_should_be_unsupported(erd: Erd, data_source: DataSource) -> None:
    """Assert that the ERD exists but is listed as unsupported."""
    assert data_source._data["test"]["unsupported_erds"].get(erd) is not None


def the_erd_should_be_supported(erd: Erd, data_source: DataSource) -> None:
    """Assert that the ERD exists but and is listed as supported."""
    assert data_source._data["test"]["supported_erds"].get(erd) is not None


def the_error_log_should_be(msg: str, caplog: pytest.LogCaptureFixture) -> None:
    """Assert that the given message is the only logged error."""
    assert caplog.record_tuples == [
        (
            "custom_components.geappliances.discovery",
            logging.ERROR,
            msg,
        )
    ]


class TestDiscovery:
    """Hold discovery tests."""

    async def test_discovers_new_device(self, registry_updater_mock, discovery) -> None:
        """Test discovery discovers new appliance."""
        await when_the_device_is_discovered(discovery)

        the_device_should_exist(registry_updater_mock)

    async def test_does_not_create_entity_until_appliance_api_confirms(
        self, registry_updater_mock, data_source, discovery
    ) -> None:
        """Test discovery waits to create an entity until the appliance API confirms that ERD is supported."""
        await when_the_erd_is_set_to(0x0001, bytes.fromhex("01"), discovery)
        the_device_should_exist(registry_updater_mock)
        the_entity_should_not_exist("Test: Test", registry_updater_mock)
        the_erd_should_be_unsupported(0x0001, data_source)

        await when_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0001 0000 0000"), discovery
        )
        the_erd_should_be_supported(0x0001, data_source)
        the_entity_should_be_added_to_the_device("Test: Test", registry_updater_mock)

    async def test_discovers_common_appliance_api(
        self, registry_updater_mock, data_source, discovery
    ) -> None:
        """Test discovery discovers common appliance API and sets up sensors."""
        await when_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0001 0000 0001"), discovery
        )

        the_erd_should_be_supported(0x0001, data_source)
        the_entity_should_be_added_to_the_device("Test: Test", registry_updater_mock)

        the_erd_should_be_supported(0x0002, data_source)
        the_entity_should_be_added_to_the_device(
            "Another Test: Another Test", registry_updater_mock
        )

    async def test_discovers_feature_appliance_api(
        self, registry_updater_mock, discovery
    ) -> None:
        """Test discovery discovers feature appliance API and sets up sensors."""
        await when_the_erd_is_set_to(
            0x0093, bytes.fromhex("0000 0001 0000 0001"), discovery
        )
        the_entity_should_be_added_to_the_device(
            "Feature Test: Feature Test", registry_updater_mock
        )
        the_entity_should_be_added_to_the_device(
            "Another Feature Test: Another Feature Test", registry_updater_mock
        )

    async def test_does_not_create_multiple_sensors_for_same_erd(
        self, registry_updater_mock, discovery
    ) -> None:
        """Test discovery does not set up sensors multiple times for an existing ERD."""
        await when_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0001 0000 0001"), discovery
        )
        the_entity_should_be_added_to_the_device("Test: Test", registry_updater_mock)
        the_entity_should_be_added_to_the_device(
            "Another Test: Another Test", registry_updater_mock
        )

        await when_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0001 0000 0001"), discovery
        )
        the_entity_should_not_exist("Test: Test_2", registry_updater_mock)
        the_entity_should_not_exist(
            "Another Test: Another Test_2", registry_updater_mock
        )

    async def test_creates_sensor_for_each_field(
        self, registry_updater_mock, discovery
    ) -> None:
        """Test discovery sets up a sensor for each field in the ERD."""
        await when_the_erd_is_set_to(
            0x0093, bytes.fromhex("0001 0001 0000 0000"), discovery
        )
        the_entity_should_be_added_to_the_device(
            "Multi Field Test: Field One", registry_updater_mock
        )
        the_entity_should_be_added_to_the_device(
            "Multi Field Test: Field Two", registry_updater_mock
        )

    async def test_moves_erds_to_unsupported_when_appliance_api_changes(
        self, data_source, discovery
    ) -> None:
        """Test discovery moves ERDs to the unsupported list when the appliance API manifest no longer lists them as supported."""
        await given_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0001 0000 0001"), discovery
        )

        await when_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0001 0000 0000"), discovery
        )
        the_erd_should_be_supported(0x0001, data_source)
        the_erd_should_be_unsupported(0x0002, data_source)

    async def test_logs_when_common_appliance_api_is_bad(
        self, capture_errors, discovery
    ) -> None:
        """Test discovery logs an error for a bad common appliance API version."""
        await when_the_erd_is_set_to(
            0x0092, bytes.fromhex("0000 0002 0000 0000"), discovery
        )
        the_error_log_should_be(
            "Invalid common appliance API version: 2", capture_errors
        )

    async def test_logs_when_feature_appliance_api_is_bad(
        self, capture_errors, discovery
    ) -> None:
        """Test discovery logs an error for a bad feature appliance API version."""
        await when_the_erd_is_set_to(
            0x0093, bytes.fromhex("0000 0002 0000 0000"), discovery
        )
        the_error_log_should_be(
            "Invalid feature appliance API: (type: 0 version: 2)", capture_errors
        )
