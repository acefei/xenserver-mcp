"""Unit tests for Storage management tools."""

from unittest.mock import Mock, patch

import pytest

from xenserver_mcp.helpers import resolve_sr, validate_positive_int
from xenserver_mcp.server import get_sr_info, list_storage_repositories

from .conftest import MockSR, parse_json_result


class TestListStorageRepositories:
    """Test list_storage_repositories tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.SR")
    def test_list_srs_success(self, mock_sr_class, mock_session_ctx, mock_config):
        """Test successful SR listing."""
        mock_config.return_value = {"test-cluster": {}}

        sr1 = MockSR(uuid="sr-1", name="LocalStorage")
        sr2 = MockSR(uuid="sr-2", name="SharedStorage")

        mock_sr_class.get_all.return_value = [sr1, sr2]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_storage_repositories("test-cluster")

        result_obj = parse_json_result(result)
        assert len(result_obj) == 2
        assert result_obj[0]["name"] == "LocalStorage"
        assert result_obj[0]["uuid"] == "sr-1"
        assert result_obj[0]["type"] == "lvm"
        assert result_obj[1]["name"] == "SharedStorage"

    @patch("xenserver_mcp.server.load_cluster_config")
    def test_list_srs_invalid_cluster(self, mock_config):
        """Test list_storage_repositories with invalid cluster ID."""
        mock_config.return_value = {"other-cluster": {}}

        result = list_storage_repositories("invalid-cluster")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "invalid-cluster" in result_obj["error"]

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.SR")
    def test_list_srs_empty(self, mock_sr_class, mock_session_ctx, mock_config):
        """Test list_storage_repositories with no SRs."""
        mock_config.return_value = {"test-cluster": {}}
        mock_sr_class.get_all.return_value = []

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_storage_repositories("test-cluster")

        result_obj = parse_json_result(result)
        assert isinstance(result_obj, list)
        assert len(result_obj) == 0


class TestGetSRInfo:
    """Test get_sr_info tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_sr")
    def test_get_sr_info_success(self, mock_resolve, mock_session_ctx, mock_config):
        """Test successful SR info retrieval."""
        mock_config.return_value = {"test-cluster": {}}

        sr = MockSR(uuid="test-sr", name="TestStorage")
        mock_resolve.return_value = sr

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_sr_info("test-cluster", "test-sr")

        result_obj = parse_json_result(result)
        assert result_obj["uuid"] == "test-sr"
        assert result_obj["name"] == "TestStorage"
        assert result_obj["type"] == "lvm"
        assert result_obj["physical_size"] == 1099511627776

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_sr")
    def test_get_sr_info_not_found(self, mock_resolve, mock_session_ctx, mock_config):
        """Test get_sr_info with non-existent SR."""
        mock_config.return_value = {"test-cluster": {}}
        mock_resolve.return_value = None

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_sr_info("test-cluster", "nonexistent-sr")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "not found" in result_obj["error"]
        assert result_obj["code"] == "resource_not_found"


class TestResolveSR:
    """Test resolve_sr helper function."""

    def test_resolve_sr_by_uuid(self, mock_session):
        """Test resolving SR by UUID."""
        sr = MockSR(uuid="test-uuid")

        with patch("xenserver_mcp.helpers.SR") as mock_sr_class:
            mock_sr_class.get_by_uuid.return_value = sr

            result = resolve_sr(mock_session, "test-uuid")

            assert result is not None
            assert result.get_uuid() == "test-uuid"

    def test_resolve_sr_by_name(self, mock_session):
        """Test resolving SR by name."""
        sr = MockSR(name="TestStorage")

        mock_session.xenapi.SR.get_by_name_label.return_value = ["OpaqueRef:sr-1"]

        with patch("xenserver_mcp.helpers.SR") as mock_sr_class:
            mock_sr_class.get_by_uuid.return_value = None
            mock_sr_class.return_value = sr

            result = resolve_sr(mock_session, "TestStorage")

            assert result is not None
            assert result.get_name() == "TestStorage"

    def test_resolve_sr_not_found(self, mock_session):
        """Test resolving non-existent SR."""
        with patch("xenserver_mcp.helpers.SR") as mock_sr_class:
            mock_sr_class.get_by_uuid.return_value = None
            mock_session.xenapi.SR.get_by_name_label.return_value = []

            result = resolve_sr(mock_session, "nonexistent")

            assert result is None


class TestValidatePositiveInt:
    """Test validate_positive_int helper function."""

    def test_validate_positive_int_valid(self):
        """Test validation with valid positive integer."""
        result = validate_positive_int(42, "size")
        assert result is None

    def test_validate_positive_int_zero(self):
        """Test validation with zero."""
        result = validate_positive_int(0, "size")
        assert result is not None
        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "positive integer" in result_obj["error"].lower()

    def test_validate_positive_int_negative(self):
        """Test validation with negative integer."""
        result = validate_positive_int(-10, "size")
        assert result is not None
        result_obj = parse_json_result(result)
        assert "error" in result_obj

    def test_validate_positive_int_not_int(self):
        """Test validation with non-integer."""
        result = validate_positive_int("not-an-int", "size")
        assert result is not None
        result_obj = parse_json_result(result)
        assert "error" in result_obj


class TestStorageErrorHandling:
    """Test error handling in storage tools."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.SR")
    def test_list_srs_partial_failure(
        self, mock_sr_class, mock_session_ctx, mock_config
    ):
        """Test list_storage_repositories handles partial failures."""
        mock_config.return_value = {"test-cluster": {}}

        # Create a good SR and a bad SR
        good_sr = MockSR(uuid="sr-1", name="GoodSR")

        bad_sr = Mock()
        bad_sr.serialize.side_effect = RuntimeError("SR unavailable")

        mock_sr_class.get_all.return_value = [good_sr, bad_sr]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_storage_repositories("test-cluster")

        # Should skip the bad SR and return the good one
        result_obj = parse_json_result(result)
        assert len(result_obj) == 1
        assert result_obj[0]["name"] == "GoodSR"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_sr")
    def test_get_sr_info_exception(self, mock_resolve, mock_session_ctx, mock_config):
        """Test get_sr_info handles exceptions gracefully."""
        mock_config.return_value = {"test-cluster": {}}

        # Create an SR that raises an exception
        sr = MockSR(uuid="test-sr", name="TestSR")

        def raise_error():
            raise RuntimeError("Storage error")

        sr.serialize = raise_error
        mock_resolve.return_value = sr

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_sr_info("test-cluster", "test-sr")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert result_obj["code"] == "operation_failed"
