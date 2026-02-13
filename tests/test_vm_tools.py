"""Unit tests for VM management tools."""

from unittest.mock import Mock, patch

import pytest

from xenserver_mcp.helpers import (
    format_error,
    format_success,
    resolve_vm,
    retry_async,
    validate_cluster_id,
    validate_required,
)
from xenserver_mcp.server import (
    get_vm_info,
    list_vm_templates,
    list_vms,
    start_vm,
)

from .conftest import MockVM, parse_json_result


class TestListVMs:
    """Test list_vms tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.VM")
    def test_list_vms_success(self, mock_vm_class, mock_session_ctx, mock_config):
        """Test successful VM listing."""
        # Setup mock configuration
        mock_config.return_value = {"test-cluster": {}}

        # Setup mock VMs
        vm1 = MockVM(uuid="vm-1", name="TestVM1", power_state="Running")
        vm2 = MockVM(uuid="vm-2", name="TestVM2", power_state="Halted")

        # Mock VM.list_vm to return our mock VMs
        mock_vm_class.list_vm.return_value = [vm1, vm2]

        # Mock session context manager
        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        # Call the tool
        result = list_vms("test-cluster")

        # Verify result is valid JSON
        result_obj = parse_json_result(result)
        assert len(result_obj) == 2
        assert result_obj[0]["name"] == "TestVM1"
        assert result_obj[0]["uuid"] == "vm-1"
        assert result_obj[0]["power_state"] == "Running"
        assert result_obj[1]["name"] == "TestVM2"
        assert result_obj[1]["power_state"] == "Halted"

    @patch("xenserver_mcp.server.load_cluster_config")
    def test_list_vms_invalid_cluster(self, mock_config):
        """Test list_vms with invalid cluster ID."""
        mock_config.return_value = {"other-cluster": {}}

        result = list_vms("invalid-cluster")

        # Should return formatted error
        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "invalid-cluster" in result_obj["error"]
        assert result_obj["code"] == "cluster_not_found"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.VM")
    def test_list_vms_empty(self, mock_vm_class, mock_session_ctx, mock_config):
        """Test list_vms with no VMs."""
        mock_config.return_value = {"test-cluster": {}}
        mock_vm_class.list_vm.return_value = []

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_vms("test-cluster")

        result_obj = parse_json_result(result)
        assert isinstance(result_obj, list)
        assert len(result_obj) == 0


class TestGetVMInfo:
    """Test get_vm_info tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_vm")
    def test_get_vm_info_success(self, mock_resolve, mock_session_ctx, mock_config):
        """Test successful VM info retrieval."""
        mock_config.return_value = {"test-cluster": {}}

        vm = MockVM(uuid="test-vm", name="TestVM")
        mock_resolve.return_value = vm

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_vm_info("test-cluster", "test-vm")

        result_obj = parse_json_result(result)
        assert result_obj["uuid"] == "test-vm"
        assert result_obj["name_label"] == "TestVM"
        assert result_obj["power_state"] == "Running"

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_vm")
    def test_get_vm_info_not_found(self, mock_resolve, mock_session_ctx, mock_config):
        """Test get_vm_info with non-existent VM."""
        mock_config.return_value = {"test-cluster": {}}
        mock_resolve.return_value = None

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = get_vm_info("test-cluster", "nonexistent-vm")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "not found" in result_obj["error"]
        assert result_obj["code"] == "resource_not_found"

    @patch("xenserver_mcp.server.load_cluster_config")
    def test_get_vm_info_empty_identifier(self, mock_config):
        """Test get_vm_info with empty identifier."""
        mock_config.return_value = {"test-cluster": {}}

        result = get_vm_info("test-cluster", "")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "required" in result_obj["error"].lower()


class TestListVMTemplates:
    """Test list_vm_templates tool."""

    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.VM")
    def test_list_templates_success(self, mock_vm_class, mock_session_ctx, mock_config):
        """Test successful template listing."""
        mock_config.return_value = {"test-cluster": {}}

        template1 = MockVM(uuid="tmpl-1", name="Ubuntu 22.04")
        template1._description = "Ubuntu 22.04 LTS Template"
        template2 = MockVM(uuid="tmpl-2", name="CentOS 8")
        template2._description = "CentOS 8 Template"

        mock_vm_class.list_templates.return_value = [template1, template2]

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = list_vm_templates("test-cluster")

        result_obj = parse_json_result(result)
        assert len(result_obj) == 2
        assert result_obj[0]["name"] == "Ubuntu 22.04"
        assert result_obj[0]["uuid"] == "tmpl-1"
        assert result_obj[1]["name"] == "CentOS 8"


class TestStartVM:
    """Test start_vm tool (async operation with retry)."""

    @pytest.mark.asyncio
    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_vm")
    @patch("xenserver_mcp.server.retry_async")
    async def test_start_vm_success(
        self, mock_retry, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test successful VM start operation."""
        mock_config.return_value = {"test-cluster": {}}

        vm = MockVM(uuid="test-vm", name="TestVM", power_state="Halted")
        mock_resolve.return_value = vm

        # Mock retry_async to just call the function
        async def mock_retry_fn(fn):
            return await fn()

        mock_retry.side_effect = mock_retry_fn

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = await start_vm("test-cluster", "test-vm")

        assert "Success" in result
        assert "TestVM" in result
        assert "started" in result

    @pytest.mark.asyncio
    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    @patch("xenserver_mcp.server.resolve_vm")
    async def test_start_vm_not_found(
        self, mock_resolve, mock_session_ctx, mock_config
    ):
        """Test start_vm with non-existent VM."""
        mock_config.return_value = {"test-cluster": {}}
        mock_resolve.return_value = None

        mock_session = Mock()
        mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

        result = await start_vm("test-cluster", "nonexistent-vm")

        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "not found" in result_obj["error"]


class TestHelperFunctions:
    """Test helper functions used by VM tools."""

    def test_resolve_vm_by_uuid(self, mock_session):
        """Test resolving VM by UUID."""
        vm = MockVM(uuid="test-uuid")

        # Mock VM.get_by_uuid to return our mock VM
        with patch("xenserver_mcp.helpers.VM") as mock_vm_class:
            mock_vm_class.get_by_uuid.return_value = vm

            result = resolve_vm(mock_session, "test-uuid")

            assert result is not None
            assert result.get_uuid() == "test-uuid"

    def test_resolve_vm_by_name(self, mock_session):
        """Test resolving VM by name."""
        vm = MockVM(name="TestVM")

        # Mock session to return VM ref by name
        mock_session.xenapi.VM.get_by_name_label.return_value = ["OpaqueRef:vm-1"]

        with patch("xenserver_mcp.helpers.VM") as mock_vm_class:
            mock_vm_class.get_by_uuid.return_value = None
            mock_vm_class.return_value = vm

            result = resolve_vm(mock_session, "TestVM")

            assert result is not None
            assert result.get_name() == "TestVM"

    def test_resolve_vm_not_found(self, mock_session):
        """Test resolving non-existent VM."""
        with patch("xenserver_mcp.helpers.VM") as mock_vm_class:
            mock_vm_class.get_by_uuid.return_value = None
            mock_session.xenapi.VM.get_by_name_label.return_value = []

            result = resolve_vm(mock_session, "nonexistent")

            assert result is None

    def test_validate_cluster_id_valid(self, mock_config):
        """Test cluster validation with valid ID."""
        result = validate_cluster_id(mock_config, "test-cluster")
        assert result is None

    def test_validate_cluster_id_invalid(self, mock_config):
        """Test cluster validation with invalid ID."""
        result = validate_cluster_id(mock_config, "invalid")
        assert result is not None
        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert result_obj["code"] == "cluster_not_found"

    def test_validate_required_valid(self):
        """Test required validation with valid value."""
        result = validate_required("test-value", "field")
        assert result is None

    def test_validate_required_empty(self):
        """Test required validation with empty value."""
        result = validate_required("", "field")
        assert result is not None
        result_obj = parse_json_result(result)
        assert "error" in result_obj
        assert "required" in result_obj["error"].lower()

    def test_format_success_dict(self):
        """Test formatting successful response with dict."""
        data = {"key": "value", "count": 42}
        result = format_success(data, "Test message")

        assert "Test message" in result
        result_lines = result.split("\n", 1)
        result_obj = parse_json_result(result)
        assert result_obj["key"] == "value"
        assert result_obj["count"] == 42

    def test_format_error_basic(self):
        """Test formatting error response."""
        result = format_error("Something went wrong", code="test_error")

        result_obj = parse_json_result(result)
        assert result_obj["error"] == "Something went wrong"
        assert result_obj["code"] == "test_error"


class TestRetryAsync:
    """Test async retry logic."""

    @pytest.mark.asyncio
    async def test_retry_async_success_first_attempt(self):
        """Test retry succeeds on first attempt."""
        call_count = 0

        async def success_fn():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_async(success_fn, attempts=3)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_success_after_retry(self):
        """Test retry succeeds after failures."""
        call_count = 0

        async def flaky_fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"

        result = await retry_async(
            flaky_fn, attempts=3, delay_seconds=0.01, retry_exceptions=(ValueError,)
        )

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_all_attempts_fail(self):
        """Test retry exhausts all attempts."""
        call_count = 0

        async def always_fail_fn():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            await retry_async(
                always_fail_fn,
                attempts=3,
                delay_seconds=0.01,
                retry_exceptions=(ValueError,),
            )

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_wrong_exception(self):
        """Test retry fails immediately on unexpected exception."""
        call_count = 0

        async def wrong_error_fn():
            nonlocal call_count
            call_count += 1
            raise TypeError("Wrong exception type")

        with pytest.raises(TypeError, match="Wrong exception type"):
            await retry_async(
                wrong_error_fn, attempts=3, retry_exceptions=(ValueError,)
            )

        # Should fail immediately, not retry
        assert call_count == 1
