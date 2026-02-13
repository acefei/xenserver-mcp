# XenServer MCP Server Tests

This directory contains unit tests for the XenServer MCP Server. The tests use mock XenAPI sessions to verify tool behavior without requiring real XenServer infrastructure.

## Test Structure

```
tests/
├── __init__.py                  # Package marker
├── conftest.py                  # Shared pytest fixtures and mock classes
├── test_vm_tools.py            # VM management tool tests
├── test_host_tools.py          # Host management tool tests
├── test_storage_tools.py       # Storage management tool tests
└── test_network_tools.py       # Network management tool tests
```

## Test Coverage

### VM Tools (`test_vm_tools.py`)
- List VMs with various filters
- Get VM info and handle errors
- List VM templates
- Start VM (async operation with retry logic)
- Validate VM resolution by UUID and name
- Test error handling and validation

### Host Tools (`test_host_tools.py`)
- List hosts in cluster
- Get detailed host information
- Get host metrics (CPU, memory)
- Get host capabilities
- Test host resolution and error handling

### Storage Tools (`test_storage_tools.py`)
- List storage repositories
- Get SR details and usage
- Test SR resolution by UUID and name
- Validate positive integers (for sizes)
- Test partial failures and error handling

### Network Tools (`test_network_tools.py`)
- List virtual networks
- Get network details
- Test network resolution
- Test error handling and partial failures
- Integration test for typical workflows

## Running Tests

### Install Test Dependencies

```bash
# Install all dev dependencies including pytest
uv sync --all-groups
```

### Run All Tests

```bash
# Run all tests with verbose output
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/xenserver_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_vm_tools.py -v

# Run specific test class
uv run pytest tests/test_vm_tools.py::TestListVMs -v

# Run specific test
uv run pytest tests/test_vm_tools.py::TestListVMs::test_list_vms_success -v
```

### Run Tests by Category

```bash
# VM tests only
uv run pytest tests/test_vm_tools.py -v

# Host tests only
uv run pytest tests/test_host_tools.py -v

# Storage tests only
uv run pytest tests/test_storage_tools.py -v

# Network tests only
uv run pytest tests/test_network_tools.py -v
```

### Run Async Tests

The async tests (e.g., `test_start_vm_success`) are automatically handled by `pytest-asyncio`:

```bash
# Run all async tests
uv run pytest tests/ -k "async" -v

# Run specific async test
uv run pytest tests/test_vm_tools.py::TestStartVM -v
```

## Mock Architecture

### Mock XenAPI Session (`conftest.py`)

The `MockXenAPISession` class provides a fake XenAPI session that:
- Mimics the structure of a real XenAPI session
- Returns predictable data for testing
- Doesn't make network calls
- Can be configured per-test

### Mock Resource Classes

Each resource type has a corresponding mock class:
- `MockVM` - Virtual Machine
- `MockHost` - XenServer Host
- `MockSR` - Storage Repository
- `MockNetwork` - Virtual Network

These mocks:
- Implement the same interface as real wrapper classes
- Return consistent test data
- Support both sync and async operations
- Can be configured for error scenarios

## Test Patterns

### Testing Successful Operations

```python
@patch("xenserver_mcp.server.load_cluster_config")
@patch("xenserver_mcp.server.xapi_session")
@patch("xenserver_mcp.server.VM")
def test_list_vms_success(mock_vm_class, mock_session_ctx, mock_config):
    # Setup mocks
    mock_config.return_value = {"test-cluster": {}}
    vm1 = MockVM(uuid="vm-1", name="TestVM1")
    mock_vm_class.list_vm.return_value = [vm1]
    
    # Mock session context manager
    mock_session = Mock()
    mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
    mock_session_ctx.return_value.__exit__ = Mock(return_value=False)
    
    # Execute and verify
    result = list_vms("test-cluster")
    result_obj = json.loads(result)
    assert result_obj[0]["name"] == "TestVM1"
```

### Testing Error Handling

```python
def test_list_vms_invalid_cluster(mock_config):
    mock_config.return_value = {"other-cluster": {}}
    
    result = list_vms("invalid-cluster")
    
    result_obj = json.loads(result)
    assert "error" in result_obj
    assert result_obj["code"] == "cluster_not_found"
```

### Testing Async Operations

```python
@pytest.mark.asyncio
@patch("xenserver_mcp.server.retry_async")
async def test_start_vm_success(mock_retry, ...):
    # Mock retry_async to just call the function
    async def mock_retry_fn(fn):
        return await fn()
    mock_retry.side_effect = mock_retry_fn
    
    result = await start_vm("test-cluster", "test-vm")
    assert "Success" in result
```

### Testing Retry Logic

```python
@pytest.mark.asyncio
async def test_retry_async_success_after_retry():
    call_count = 0
    
    async def flaky_fn():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Transient error")
        return "success"
    
    result = await retry_async(flaky_fn, attempts=3)
    assert result == "success"
    assert call_count == 3
```

## Key Features Tested

1. **Validation** - All input validation (cluster ID, required fields, positive integers)
2. **Resource Resolution** - Finding resources by UUID or name
3. **Error Handling** - Graceful handling of missing resources and exceptions
4. **Partial Failures** - Tools handle partial failures in list operations
5. **Async Operations** - Proper async/await handling with retry logic
6. **Data Formatting** - JSON output format consistency

## Notes

- Tests are fast and deterministic (no network calls)
- Each test is isolated with its own mock setup
- Mock fixtures are reusable across tests
- Tests verify both successful operations and error cases
- Coverage includes key flows without exhaustive combinations
- Async tests use `pytest.mark.asyncio` decorator

## Adding New Tests

When adding new tests:

1. **Add mock classes to `conftest.py`** if testing new resource types
2. **Follow existing patterns** for consistency
3. **Test both success and error cases**
4. **Use descriptive test names** that explain what is being tested
5. **Mock at the right level** - session, wrapper classes, or helpers
6. **Keep tests focused** - one behavior per test

Example:

```python
class TestNewTool:
    """Test new_tool functionality."""
    
    @patch("xenserver_mcp.server.load_cluster_config")
    @patch("xenserver_mcp.server.xapi_session")
    def test_new_tool_success(self, mock_session_ctx, mock_config):
        """Test successful new_tool operation."""
        # Setup, execute, verify
        pass
    
    def test_new_tool_validation_error(self):
        """Test new_tool with invalid input."""
        # Test validation logic
        pass
```
