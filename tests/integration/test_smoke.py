"""Smoke tests for XenServer MCP Server integration.

These tests verify basic connectivity and core functionality against a real XCP-ng environment.
They are skipped by default and only run when XENSERVER_INTEGRATION=1 is set.
"""

import os

import pytest

# Skip all tests in this module unless XENSERVER_INTEGRATION=1
pytestmark = pytest.mark.skipif(
    os.getenv("XENSERVER_INTEGRATION") != "1",
    reason="Integration tests require XENSERVER_INTEGRATION=1 environment variable",
)


@pytest.fixture
def test_cluster_id() -> str:
    """Return the test cluster ID from configuration."""
    return "test"


@pytest.fixture
def config_path() -> str | None:
    """Return the path to the configuration file."""
    return os.getenv("XENSERVER_CONFIG")


class TestConnection:
    """Test basic connection functionality."""

    def test_config_file_exists(self, config_path: str | None) -> None:
        """Verify configuration file exists."""
        assert config_path is not None, "XENSERVER_CONFIG environment variable not set"
        import json
        from pathlib import Path

        config_file = Path(config_path)
        assert config_file.exists(), f"Configuration file not found: {config_path}"

        # Verify it's valid JSON
        with config_file.open() as f:
            config = json.load(f)

        assert isinstance(config, dict), "Configuration must be a JSON object"

    def test_test_cluster_exists(self, config_path: str | None) -> None:
        """Verify test cluster is configured."""
        import json
        from pathlib import Path

        assert config_path is not None
        with Path(config_path).open() as f:
            config = json.load(f)

        assert "test" in config, "Configuration must include a 'test' cluster"
        test_config = config["test"]
        assert "host" in test_config, "Test cluster must have 'host' field"
        assert "username" in test_config, "Test cluster must have 'username' field"
        assert "password" in test_config, "Test cluster must have 'password' field"

    def test_can_load_config(self, test_cluster_id: str) -> None:
        """Test that configuration can be loaded."""
        from xenserver_mcp.config import load_cluster_config

        config = load_cluster_config()
        assert isinstance(config, dict), "Configuration must be a dictionary"
        assert test_cluster_id in config, f"Cluster '{test_cluster_id}' not found"

    def test_can_create_session(self, test_cluster_id: str) -> None:
        """Test that a session can be created to the test cluster."""
        from xen_api.session import xapi_session
        from xenserver_mcp.config import load_cluster_config

        config = load_cluster_config()

        # Try to create a session - this will fail if credentials are wrong
        # or if the host is unreachable
        try:
            with xapi_session(test_cluster_id, config) as session:
                assert session is not None, "Session should not be None"
                # Try a simple API call to verify session works
                pools = session.xenapi.pool.get_all()
                assert len(pools) > 0, (
                    "Should have at least one pool (test environment)"
                )
        except Exception as e:
            pytest.fail(
                f"Failed to create session or query pool: {e!s}. "
                "Check credentials and network connectivity."
            )


class TestBasicOperations:
    """Test basic MCP operations against real infrastructure."""

    def test_list_clusters(self) -> None:
        """Test list_clusters tool."""
        from xenserver_mcp.server import list_clusters

        result = list_clusters()
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        # Should contain the test cluster
        assert "test" in result.lower(), "Should list the test cluster"

    def test_list_vms(self, test_cluster_id: str) -> None:
        """Test list_vms tool."""
        from xenserver_mcp.server import list_vms

        result = list_vms(cluster_id=test_cluster_id)
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        # Result should be valid JSON or descriptive text
        assert "{" in result or "VM" in result or "No VMs" in result, (
            "Result should contain VM information or 'No VMs' message"
        )

    def test_list_hosts(self, test_cluster_id: str) -> None:
        """Test list_hosts tool."""
        from xenserver_mcp.server import list_hosts

        result = list_hosts(cluster_id=test_cluster_id)
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        # Should have at least one host in test environment
        assert "host" in result.lower(), "Result should contain host information"

    def test_get_pool_info(self, test_cluster_id: str) -> None:
        """Test get_pool_info tool."""
        from xenserver_mcp.server import get_pool_info

        result = get_pool_info(cluster_id=test_cluster_id)
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        assert "pool" in result.lower(), "Result should contain pool information"

    def test_list_storage_repositories(self, test_cluster_id: str) -> None:
        """Test list_storage_repositories tool."""
        from xenserver_mcp.server import list_storage_repositories

        result = list_storage_repositories(cluster_id=test_cluster_id)
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        # Should have at least one SR in test environment
        assert "SR" in result or "storage" in result.lower(), (
            "Result should contain storage information"
        )

    def test_list_networks(self, test_cluster_id: str) -> None:
        """Test list_networks tool."""
        from xenserver_mcp.server import list_networks

        result = list_networks(cluster_id=test_cluster_id)
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        # Should have at least one network in test environment
        assert "network" in result.lower(), "Result should contain network information"


class TestErrorHandling:
    """Test error handling with invalid inputs."""

    def test_invalid_cluster_id(self) -> None:
        """Test that invalid cluster ID is handled gracefully."""
        from xenserver_mcp.server import list_vms

        result = list_vms(cluster_id="nonexistent-cluster-12345")
        assert isinstance(result, str), "Result should be a string"
        assert "error" in result.lower() or "not found" in result.lower(), (
            "Should return error message for invalid cluster"
        )

    def test_invalid_vm_identifier(self, test_cluster_id: str) -> None:
        """Test that invalid VM identifier is handled gracefully."""
        from xenserver_mcp.server import get_vm_info

        result = get_vm_info(
            cluster_id=test_cluster_id,
            vm_identifier="nonexistent-vm-uuid-12345",
        )
        assert isinstance(result, str), "Result should be a string"
        assert "error" in result.lower() or "not found" in result.lower(), (
            "Should return error message for invalid VM"
        )

    def test_invalid_host_identifier(self, test_cluster_id: str) -> None:
        """Test that invalid host identifier is handled gracefully."""
        from xenserver_mcp.server import get_host_info

        result = get_host_info(
            cluster_id=test_cluster_id,
            host_identifier="nonexistent-host-uuid-12345",
        )
        assert isinstance(result, str), "Result should be a string"
        assert "error" in result.lower() or "not found" in result.lower(), (
            "Should return error message for invalid host"
        )
