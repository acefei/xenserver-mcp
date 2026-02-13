# Integration Tests

This directory contains integration tests for the XenServer MCP Server that require a real XCP-ng/XenServer environment.

## Prerequisites

- A running XCP-ng or XenServer host/pool
- Valid credentials with appropriate permissions
- Network connectivity to the XenServer host

## Configuration

Integration tests require the following environment variables:

### Required Variables

- `XENSERVER_INTEGRATION=1` - Enable integration tests (tests are skipped if not set)
- `XENSERVER_CONFIG` - Path to clusters.json configuration file

### Configuration File Format

Create a `config/clusters.json` file with your test environment:

```json
{
  "test": {
    "host": "xenserver-test.example.com",
    "username": "root",
    "password": "your-test-password"
  }
}
```

**Security Note**: Never commit real credentials to version control. Use a separate test configuration file that is gitignored.

## Running Integration Tests

### Run All Integration Tests

```bash
# Set required environment variables
export XENSERVER_INTEGRATION=1
export XENSERVER_CONFIG=/path/to/test/clusters.json

# Run integration tests
uv run pytest tests/integration/ -v
```

### Run Specific Test File

```bash
export XENSERVER_INTEGRATION=1
export XENSERVER_CONFIG=/path/to/test/clusters.json

uv run pytest tests/integration/test_smoke.py -v
```

### Skip Integration Tests (Default)

Integration tests are automatically skipped when `XENSERVER_INTEGRATION` is not set to `1`:

```bash
# These will skip integration tests
uv run pytest tests/
pytest tests/
```

## CI/CD Behavior

Integration tests are **skipped by default** in the CI pipeline because:

1. They require real infrastructure (not available in CI runners)
2. They require credentials (security risk in CI)
3. They are slower than unit tests

Unit tests are run in CI, integration tests should be run manually against test environments.

## Writing Integration Tests

When adding new integration tests:

1. Always use the `@pytest.mark.skipif` decorator to skip when `XENSERVER_INTEGRATION != "1"`
2. Use the test cluster configuration (cluster_id = "test")
3. Clean up any resources created during tests
4. Handle connection errors gracefully
5. Document any specific environment requirements

Example:

```python
import os
import pytest

@pytest.mark.skipif(
    os.getenv("XENSERVER_INTEGRATION") != "1",
    reason="Integration tests require XENSERVER_INTEGRATION=1"
)
def test_connection():
    """Test basic connection to XenServer."""
    # Test implementation
    pass
```

## Test Structure

- `test_smoke.py` - Basic smoke tests for connectivity and core functionality
- Add more test files as needed for specific feature areas

## Troubleshooting

### Tests Skip Unexpectedly

- Verify `XENSERVER_INTEGRATION=1` is set
- Check that environment variable is exported in your shell

### Connection Failures

- Verify XenServer host is reachable: `ping xenserver-test.example.com`
- Check credentials in configuration file
- Ensure firewall allows HTTPS (port 443)
- Verify XenServer API is accessible: `curl -k https://xenserver-test.example.com`

### Permission Errors

- Ensure user has appropriate permissions (Pool Admin recommended for tests)
- Check XenServer user account is not locked

### SSL Certificate Errors

- Integration tests typically disable SSL verification for test environments
- For production testing, ensure valid SSL certificates are configured
