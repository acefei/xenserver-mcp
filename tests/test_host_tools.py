"""Unit tests for Host management tools."""

from unittest.mock import Mock, patch

import pytest

from xenserver_mcp.helpers import resolve_host
from xenserver_mcp.server import (
    get_host_capabilities,
    get_host_info,
    get_host_metrics,
    list_hosts,
)

from .conftest import MockHost, parse_json_result


class TestListHosts:
    """Test list_hosts tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.Host")
    def test_list_hosts_success(self, mock_host_class, mock_session_ctx, mock_config):
        """Test successful host listing."""
        mock_config.return_value = {"test-cluster": {}}

        host1 = MockHost(uuid="host-1", name="Host1")
        host2 = MockHost(uuid="host-2", name="Host2")

        mock_host_class.list_host.return_value = [host1, host2]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_hosts("test-cluster")

        result_obj = parse_json_result(result)
        assert len(result_obj) == 2
        assert result_obj[0]["name"] == "Host1"
        assert result_obj[0]["uuid"] == "host-1"
        assert result_obj[0]["enabled"] is True
        assert result_obj[1]["name"] == "Host2"

    @patch("xenserver_mcp.server.load_cluster_config")
    def test_list_hosts_invalid_cluster(self, mock_config):
        """Test list_hosts with invalid cluster ID."""
        mock_config.return_value = {"other-cluster": {}}

        result = list_hosts("invalid-cluster")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "invalid-cluster" in result_obj["error"]
        assert result_obj["code"] == "cluster_not_found"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.Host")
    def test_list_hosts_empty(self, mock_host_class, mock_session_ctx, mock_config):
        """Test list_hosts with no hosts."""
        mock_config.return_value = {"test-cluster": {}}
        mock_host_class.list_host.return_value = []

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_hosts("test-cluster")

        result_obj = parse_json_result(result)
        assert isinstance(result_obj, list)
        assert len(result_obj) == 0


class TestGetHostInfo:
    """Test get_host_info tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_host")
    def test_get_host_info_success(self, mock_resolve, mock_session_ctx, mock_config):
        """Test successful host info retrieval."""
        mock_config.return_value = {"test-cluster": {}}

        host = MockHost(uuid="test-host", name="TestHost")
        mock_resolve.return_value = host

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_host_info("test-cluster", "test-host")

        result_obj = parse_json_result(result)
        assert result_obj["uuid"] == "test-host"
        assert result_obj["name"] == "TestHost"
        assert result_obj["address"] == "192.168.1.100"
        assert result_obj["enabled"] is True

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_host")
    def test_get_host_info_not_found(self, mock_resolve, mock_session_ctx, mock_config):
        """Test get_host_info with non-existent host."""
        mock_config.return_value = {"test-cluster": {}}
        mock_resolve.return_value = None

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_host_info("test-cluster", "nonexistent-host")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "not found" in result_obj["error"]
        assert result_obj["code"] == "resource_not_found"


class TestGetHostMetrics:
    """Test get_host_metrics tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_host")
    def test_get_host_metrics_success(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test successful host metrics retrieval."""
        mock_config.return_value = {"test-cluster": {}}

        host = MockHost(uuid="test-host", name="TestHost")
        mock_resolve.return_value = host

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_host_metrics("test-cluster", "test-host")

        result_obj = parse_json_result(result)
        assert result_obj["host_name"] == "TestHost"
        assert result_obj["host_uuid"] == "test-host"
        assert result_obj["free_memory_bytes"] == 8589934592
        assert result_obj["total_memory_bytes"] == 17179869184
        assert "cpu_info" in result_obj
        assert result_obj["cpu_info"]["cpu_count"] == "8"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_host")
    def test_get_host_metrics_not_found(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test get_host_metrics with non-existent host."""
        mock_config.return_value = {"test-cluster": {}}
        mock_resolve.return_value = None

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_host_metrics("test-cluster", "nonexistent-host")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "not found" in result_obj["error"]


class TestGetHostCapabilities:
    """Test get_host_capabilities tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_host")
    def test_get_host_capabilities_success(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test successful host capabilities retrieval."""
        mock_config.return_value = {"test-cluster": {}}

        host = MockHost(uuid="test-host", name="TestHost")
        mock_resolve.return_value = host

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_host_capabilities("test-cluster", "test-host")

        result_obj = parse_json_result(result)
        assert result_obj["host_name"] == "TestHost"
        assert result_obj["host_uuid"] == "test-host"
        assert "capabilities" in result_obj
        assert "hvm" in result_obj["capabilities"]
        assert "hvm_directio" in result_obj["capabilities"]


class TestResolveHost:
    """Test resolve_host helper function."""

    def test_resolve_host_by_uuid(self, mock_session):
        """Test resolving host by UUID."""
        host = MockHost(uuid="test-uuid")

        with patch("xenserver_mcp.helpers.Host") as mock_host_class:
            mock_host_class.get_by_uuid.return_value = host

            result = resolve_host(mock_session, "test-uuid")

            assert result is not None
            assert result.get_uuid() == "test-uuid"

    def test_resolve_host_by_name(self, mock_session):
        """Test resolving host by name."""
        host = MockHost(name="TestHost")

        mock_session.xenapi.host.get_by_name_label.return_value = ["OpaqueRef:host-1"]

        with patch("xenserver_mcp.helpers.Host") as mock_host_class:
            mock_host_class.get_by_uuid.return_value = None
            mock_host_class.return_value = host

            result = resolve_host(mock_session, "TestHost")

            assert result is not None
            assert result.get_name() == "TestHost"

    def test_resolve_host_not_found(self, mock_session):
        """Test resolving non-existent host."""
        with patch("xenserver_mcp.helpers.Host") as mock_host_class:
            mock_host_class.get_by_uuid.return_value = None
            mock_session.xenapi.host.get_by_name_label.return_value = []

            result = resolve_host(mock_session, "nonexistent")

            assert result is None


class TestHostErrorHandling:
    """Test error handling in host tools."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_host")
    def test_get_host_metrics_exception(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test get_host_metrics handles exceptions gracefully."""
        mock_config.return_value = {"test-cluster": {}}

        # Create a host that raises an exception
        host = MockHost(uuid="test-host", name="TestHost")

        def raise_error():
            raise RuntimeError("Network error")

        host.get_free_memory = raise_error
        mock_resolve.return_value = host

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_host_metrics("test-cluster", "test-host")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert result_obj["code"] == "operation_failed"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.Host")
    def test_list_hosts_partial_failure(
        self, mock_host_class, mock_session_ctx, mock_config
    ):
        """Test list_hosts handles partial failures."""
        mock_config.return_value = {"test-cluster": {}}

        # Create a good host and a bad host
        good_host = MockHost(uuid="host-1", name="GoodHost")

        bad_host = Mock()
        bad_host.get_record.side_effect = RuntimeError("Host unavailable")

        mock_host_class.list_host.return_value = [good_host, bad_host]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_hosts("test-cluster")

        # Should skip the bad host and return the good one
        result_obj = parse_json_result(result)
        assert len(result_obj) == 1
        assert result_obj[0]["name"] == "GoodHost"
