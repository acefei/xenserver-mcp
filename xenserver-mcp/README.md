# XenServer MCP Server

A Model Context Protocol server for XenServer/XCP-ng hypervisors using the official XenAPI library and MCP framework.

## Features

- Query XenServer/XCP-ng VMs, hosts, pools, networks, storage repositories
- Built with MCP framework for easy integration with AI assistants
- Uses official XenAPI Python library for reliable XenServer communication
- Modern Python tooling with uv for dependency management
- Minimal dependencies for better performance and security

## Development with uv

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

### Prerequisites

- Python 3.11+
- uv (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- XenServer/XCP-ng host with XAPI access

### Setup

1. Install dependencies:
   ```bash
   uv sync --no-install-project
   ```

2. Create a `.env` file with your XenServer credentials:
   ```env
   XENSERVER_HOST=your-xenserver-host.example.com
   XENSERVER_USER=root
   XENSERVER_PASS=your-xenserver-password
   ```

### Running

Run the MCP server using uv:

```bash
uv run python main.py
```

Or use the provided convenience script:

```bash
./run.sh
```

The server will start on `http://0.0.0.0:8081`

### Development

Add new dependencies:
```bash
uv add package-name
```

Add development dependencies:
```bash
uv add --group dev package-name
```

After modifying dependencies, update the lock file:
```bash
uv lock
```

The `uv.lock` file ensures reproducible builds and should be committed to version control.

### Docker

The Docker image is configured to use uv for dependency management and running the application.

## Tools

### obj_list

Retrieves XenServer/XCP-ng objects using the XenAPI.

**Parameters:**
- `obj_type` (required): Type of XenServer object (`vm`, `host`, `pool`, `network`, `sr`, `vif`, `vbd`, `pif`)
- `obj_name` (optional): Specific object name/label to retrieve details for

**Examples:**

List all VMs:
```json
{
  "obj_type": "vm"
}
```

Get specific VM details:
```json
{
  "obj_type": "vm",
  "obj_name": "my-vm-name"
}
```

List all hosts:
```json
{
  "obj_type": "host"
}
```

List storage repositories:
```json
{
  "obj_type": "sr"
}
```