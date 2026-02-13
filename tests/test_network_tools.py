"""Unit tests for Network management tools."""

from unittest.mock import Mock, patch

import pytest

from xenserver_mcp.helpers import resolve_network
from xenserver_mcp.server import get_network_info, list_networks

from .conftest import MockNetwork, parse_json_result


class TestListNetworks:
    """Test list_networks tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.Network")
    def test_list_networks_success(
        self, mock_network_class, mock_session_ctx, mock_config
    ):
        """Test successful network listing."""
        mock_config.return_value = {"test-cluster": {}}

        network1 = MockNetwork(uuid="net-1", name="Network0")
        network2 = MockNetwork(uuid="net-2", name="Network1")

        mock_network_class.get_all.return_value = [network1, network2]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_networks("test-cluster")

        result_obj = parse_json_result(result)
        assert len(result_obj) == 2
        assert result_obj[0]["name"] == "Network0"
        assert result_obj[0]["uuid"] == "net-1"
        assert result_obj[0]["description"] == "Test Network"
        assert result_obj[0]["mtu"] == 1500
        assert result_obj[1]["name"] == "Network1"

    @patch("xenserver_mcp.server.load_cluster_config")
    def test_list_networks_invalid_cluster(self, mock_config):
        """Test list_networks with invalid cluster ID."""
        mock_config.return_value = {"other-cluster": {}}

        result = list_networks("invalid-cluster")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "invalid-cluster" in result_obj["error"]
        assert result_obj["code"] == "cluster_not_found"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.Network")
    def test_list_networks_empty(
        self, mock_network_class, mock_session_ctx, mock_config
    ):
        """Test list_networks with no networks."""
        mock_config.return_value = {"test-cluster": {}}
        mock_network_class.get_all.return_value = []

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_networks("test-cluster")

        result_obj = parse_json_result(result)
        assert isinstance(result_obj, list)
        assert len(result_obj) == 0


class TestGetNetworkInfo:
    """Test get_network_info tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_network")
    def test_get_network_info_success(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test successful network info retrieval."""
        mock_config.return_value = {"test-cluster": {}}

        network = MockNetwork(uuid="test-network", name="TestNetwork")
        mock_resolve.return_value = network

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_network_info("test-cluster", "test-network")

        result_obj = parse_json_result(result)
        assert result_obj["uuid"] == "test-network"
        assert result_obj["name"] == "TestNetwork"
        assert result_obj["description"] == "Test Network"
        assert result_obj["mtu"] == 1500

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_network")
    def test_get_network_info_not_found(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test get_network_info with non-existent network."""
        mock_config.return_value = {"test-cluster": {}}
        mock_resolve.return_value = None

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_network_info("test-cluster", "nonexistent-network")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "not found" in result_obj["error"]
        assert result_obj["code"] == "resource_not_found"


class TestResolveNetwork:
    """Test resolve_network helper function."""

    def test_resolve_network_by_uuid(self, mock_session):
        """Test resolving network by UUID."""
        network = MockNetwork(uuid="test-uuid")

        with patch("xenserver_mcp.helpers.Network") as mock_network_class:
            mock_network_class.get_by_uuid.return_value = network

            result = resolve_network(mock_session, "test-uuid")

            assert result is not None
            assert result.get_uuid() == "test-uuid"

    def test_resolve_network_by_name(self, mock_session):
        """Test resolving network by name."""
        network = MockNetwork(name="TestNetwork")

        mock_session.xenapi.network.get_by_name_label.return_value = ["OpaqueRef:net-1"]

        with patch("xenserver_mcp.helpers.Network") as mock_network_class:
            mock_network_class.get_by_uuid.return_value = None
            mock_network_class.return_value = network

            result = resolve_network(mock_session, "TestNetwork")

            assert result is not None
            assert result.get_name() == "TestNetwork"

    def test_resolve_network_not_found(self, mock_session):
        """Test resolving non-existent network."""
        with patch("xenserver_mcp.helpers.Network") as mock_network_class:
            mock_network_class.get_by_uuid.return_value = None
            mock_session.xenapi.network.get_by_name_label.return_value = []

            result = resolve_network(mock_session, "nonexistent")

            assert result is None


class TestNetworkErrorHandling:
    """Test error handling in network tools."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.Network")
    def test_list_networks_partial_failure(
        self, mock_network_class, mock_session_ctx, mock_config
    ):
        """Test list_networks handles partial failures."""
        mock_config.return_value = {"test-cluster": {}}

        # Create a good network and a bad network
        good_network = MockNetwork(uuid="net-1", name="GoodNetwork")

        bad_network = Mock()
        bad_network.get_name.side_effect = RuntimeError("Network unavailable")

        mock_network_class.get_all.return_value = [good_network, bad_network]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_networks("test-cluster")

        # Should skip the bad network and return the good one
        result_obj = parse_json_result(result)
        assert len(result_obj) == 1
        assert result_obj[0]["name"] == "GoodNetwork"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_network")
    def test_get_network_info_exception(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test get_network_info handles exceptions gracefully."""
        mock_config.return_value = {"test-cluster": {}}

        # Create a network that raises an exception
        network = MockNetwork(uuid="test-net", name="TestNetwork")

        def raise_error():
            raise RuntimeError("Network error")

        network.get_name = raise_error
        mock_resolve.return_value = network

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_network_info("test-cluster", "test-net")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert result_obj["code"] == "operation_failed"


class TestNetworkToolsIntegration:
    """Integration tests for network tools with mock session."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    def test_network_workflow(self, mock_session_ctx, mock_config):
        """Test typical network workflow: list then get info."""
        mock_config.return_value = {"test-cluster": {}}

        # Create mock networks
        network1 = MockNetwork(uuid="net-1", name="Network0")
        network2 = MockNetwork(uuid="net-2", name="Network1")

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        # Test listing networks
        with patch("xenserver_mcp.server.Network") as mock_network_class:
            mock_network_class.get_all.return_value = [network1, network2]

            result = list_networks("test-cluster")
            result_obj = parse_json_result(result)

            assert len(result_obj) == 2
            network_uuid = result_obj[0]["uuid"]

        # Test getting info for first network
        with patch("xenserver_mcp.server.resolve_network") as mock_resolve:
            mock_resolve.return_value = network1

            result = get_network_info("test-cluster", network_uuid)
            result_obj = parse_json_result(result)

            assert result_obj["uuid"] == "net-1"
            assert result_obj["name"] == "Network0"
