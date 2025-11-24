# XenServer MCP Server

A Model Context Protocol (MCP) server for XenServer/XCP-ng administration. This server enables AI assistants to interact with XenServer infrastructure through natural language.

## Features

- **Multi-cluster support**: Manage multiple XenServer clusters from a single server
- **Comprehensive VM management**: List, control, snapshot, and monitor virtual machines
- **Host management**: Monitor and manage XenServer hosts
- **Storage operations**: List and manage storage repositories and virtual disks
- **Network management**: View and manage network configurations
- **Pool management**: Get pool information and statistics
- **Template management**: List and work with VM templates

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/acefei/xenserver-mcp.git
cd xenserver-mcp

# Install with uv
uv sync

# Or install in editable mode
uv pip install -e .
```

### Using uvx (No installation required)

```bash
# Run directly from the repository
uvx --from /path/to/xenserver-mcp xenserver-mcp
```

## Configuration

The server loads configuration from a JSON file. By default, it looks for `config/clusters.json` in the project directory. You can specify a custom location using the `XENSERVER_CONFIG` environment variable.

Create a configuration file:

```bash
# Copy the example configuration
cp config/clusters.json.example config/clusters.json

# Edit with your credentials
nano config/clusters.json
```

Example configuration:

```json
{
  "production": {
    "host": "xenserver1.example.com",
    "username": "root",
    "password": "your-secure-password"
  },
  "development": {
    "host": "xenserver2.example.com",
    "username": "root",
    "password": "another-password"
  }
}
```

**Security Note**: Ensure this file has restricted permissions and is not committed to version control:
```bash
chmod 600 config/clusters.json
```

## Usage

### Running Locally

```bash
# Run with default configuration (uses config/clusters.json)
xenserver-mcp

# Or run directly with uv
uv run xenserver-mcp

# Run with Python module
python -m xenserver_mcp.server

# Use custom config file via environment variable
XENSERVER_CONFIG=/path/to/custom/clusters.json xenserver-mcp
```

### Using with uvx (Recommended for Claude Desktop/VS Code)

```bash
# Run from local repository (uses default config/clusters.json)
uvx --from /path/to/xenserver-mcp xenserver-mcp

# With custom config via environment variable
XENSERVER_CONFIG=/path/to/clusters.json uvx --from /path/to/xenserver-mcp xenserver-mcp
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

**Using uvx (Recommended):**
```json
{
  "mcpServers": {
    "xenserver": {
      "command": "uvx",
      "args": [
        "--from",
        "/home/feis/repos/xenserver-mcp",
        "xenserver-mcp"
      ],
      "env": {
        "XENSERVER_CONFIG": "/path/to/your/config/clusters.json"
      }
    }
  }
}
```

## Troubleshooting

### Connection Issues

If you see "Not connected to any cluster":
1. Verify `config/clusters.json` exists and is valid JSON
2. Check cluster credentials are correct
3. Ensure XenServer host is reachable
4. Verify firewall allows HTTPS (443) connections

### Session Timeout

The server automatically reconnects on session timeout. If persistent:
1. Check XenServer logs for authentication issues
2. Verify user account has appropriate permissions
3. Check for network instability

### Permission Errors

Ensure the XenServer user has appropriate permissions:
- Pool Admin role for full management
- VM Admin role for VM operations only
- Read-only role for monitoring

## Security Considerations

1. **Credential Storage**: Configuration file contains plaintext passwords
   - Use restricted file permissions (600)
   - Never commit `config/clusters.json` to version control
   - Consider using environment variables for CI/CD
   - Keep config/ directory in .gitignore

2. **Network Security**: All communication is over HTTPS
   - Verify SSL certificates in production
   - Use VPN for remote access

3. **Audit Logging**: All operations are logged
   - Review logs regularly
   - Monitor for unexpected operations

## Contributing

Contributions are welcome! Please:
1. Follow the existing code style (ruff formatting)
2. Add tests for new features
3. Update documentation
4. Submit pull requests