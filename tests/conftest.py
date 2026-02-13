"""Pytest fixtures for XenServer MCP Server tests."""

import json

from typing import Any
from unittest.mock import MagicMock, Mock

import pytest


class MockXenAPISession:
    """Mock XenAPI session for testing without real network calls."""

    def __init__(self):
        """Initialize mock session with xenapi namespace."""
        self.xenapi = MagicMock()
        self._setup_api_methods()

    def _setup_api_methods(self):
        """Setup common XenAPI method mocks."""
        # VM methods
        self.xenapi.VM.get_by_name_label = Mock(return_value=[])
        self.xenapi.VM.get_record = Mock(return_value={})

        # Host methods
        self.xenapi.host.get_by_name_label = Mock(return_value=[])
        self.xenapi.host.get_record = Mock(return_value={})

        # SR methods
        self.xenapi.SR.get_by_name_label = Mock(return_value=[])
        self.xenapi.SR.get_record = Mock(return_value={})

        # Network methods
        self.xenapi.network.get_by_name_label = Mock(return_value=[])
        self.xenapi.network.get_record = Mock(return_value={})

        # VDI methods
        self.xenapi.VDI.get_by_name_label = Mock(return_value=[])
        self.xenapi.VDI.get_record = Mock(return_value={})

        # Pool methods
        self.xenapi.pool.get_all = Mock(return_value=["OpaqueRef:pool-1"])
        self.xenapi.pool.get_record = Mock(return_value={})


class MockVM:
    """Mock VM object for testing."""

    def __init__(self, uuid="test-vm-uuid", name="test-vm", power_state="Running"):
        """Initialize mock VM."""
        self._uuid = uuid
        self._name = name
        self._power_state = power_state
        self._description = "Test VM"
        self._session = None
        self._ref = f"OpaqueRef:{uuid}"

    def get_uuid(self) -> str:
        return self._uuid

    def get_name(self) -> str:
        return self._name

    def get_power_state(self) -> str:
        return self._power_state

    def get_description(self) -> str:
        return self._description

    def get_record(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name_label": self._name,
            "power_state": self._power_state,
            "name_description": self._description,
            "VCPUs_max": "4",
            "memory_static_max": "8589934592",
        }

    async def start(self):
        """Mock start operation."""
        self._power_state = "Running"

    async def shutdown(self):
        """Mock shutdown operation."""
        self._power_state = "Halted"

    async def force_shutdown(self):
        """Mock force shutdown operation."""
        self._power_state = "Halted"

    def get_VBDs(self):
        """Mock get VBDs."""
        return []

    def get_CDs(self):
        """Mock get CDs."""
        return []


class MockHost:
    """Mock Host object for testing."""

    def __init__(self, uuid="test-host-uuid", name="test-host"):
        """Initialize mock Host."""
        self._uuid = uuid
        self._name = name
        self._address = "192.168.1.100"
        self._enabled = True

    def get_uuid(self) -> str:
        return self._uuid

    def get_name(self) -> str:
        return self._name

    def get_address(self) -> str:
        return self._address

    def get_enabled(self) -> bool:
        return self._enabled

    def get_record(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name_label": self._name,
            "address": self._address,
            "enabled": self._enabled,
            "name_description": "Test Host",
        }

    def serialize(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name": self._name,
            "address": self._address,
            "enabled": self._enabled,
        }

    def get_free_memory(self) -> int:
        return 8589934592

    def get_total_memory(self) -> int:
        return 17179869184

    def get_cpu_info(self) -> dict[str, Any]:
        return {
            "cpu_count": "8",
            "vendor": "GenuineIntel",
            "modelname": "Intel(R) Xeon(R) CPU",
        }

    def get_capabilities(self) -> list[str]:
        return ["hvm", "hvm_directio"]


class MockSR:
    """Mock SR (Storage Repository) object for testing."""

    def __init__(self, uuid="test-sr-uuid", name="test-sr"):
        """Initialize mock SR."""
        self._uuid = uuid
        self._name = name

    def get_uuid(self) -> str:
        return self._uuid

    def get_name(self) -> str:
        return self._name

    def get_record(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name_label": self._name,
            "name_description": "Test Storage Repository",
            "physical_size": "1099511627776",
            "physical_utilisation": "549755813888",
            "type": "lvm",
        }

    def serialize(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name": self._name,
            "type": "lvm",
            "physical_size": 1099511627776,
            "physical_utilisation": 549755813888,
        }

    def get_VDIs(self) -> list[Any]:
        return []


class MockNetwork:
    """Mock Network object for testing."""

    def __init__(self, uuid="test-network-uuid", name="test-network"):
        """Initialize mock Network."""
        self._uuid = uuid
        self._name = name

    def get_uuid(self) -> str:
        return self._uuid

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return "Test Network"

    def get_mtu(self) -> int:
        return 1500

    def get_record(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name_label": self._name,
            "name_description": "Test Network",
            "bridge": "xenbr0",
            "MTU": "1500",
        }

    def serialize(self) -> dict[str, Any]:
        return {
            "uuid": self._uuid,
            "name": self._name,
            "bridge": "xenbr0",
            "mtu": 1500,
        }


def parse_json_result(result: str) -> Any:
    """Parse tool output that may include a leading message line."""
    stripped = result.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(result)

    lines = result.splitlines()
    if len(lines) <= 1:
        return json.loads(result)

    return json.loads("\n".join(lines[1:]))


@pytest.fixture
def mock_session():
    """Provide a mock XenAPI session."""
    return MockXenAPISession()


@pytest.fixture
def mock_vm():
    """Provide a mock VM object."""
    return MockVM()


@pytest.fixture
def mock_host():
    """Provide a mock Host object."""
    return MockHost()


@pytest.fixture
def mock_sr():
    """Provide a mock SR object."""
    return MockSR()


@pytest.fixture
def mock_network():
    """Provide a mock Network object."""
    return MockNetwork()


@pytest.fixture
def mock_config():
    """Provide a mock cluster configuration."""
    return {
        "test-cluster": {
            "host": "xenserver.test.local",
            "username": "root",
            "password": "testpass",
        },
        "prod-cluster": {
            "host": "xenserver.prod.local",
            "username": "admin",
            "password": "prodpass",
        },
    }
