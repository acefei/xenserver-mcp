#!/bin/bash
# Simple script to run the XenServer MCP server with uv

echo "Starting XenServer MCP Server..."
cd "$(dirname "$0")" || exit 1

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one with your XenServer credentials:"
    echo "XENSERVER_HOST=your-xenserver-ip"
    echo "XENSERVER_USER=your-username"
    echo "XENSERVER_PASS=your-password"
    echo ""
fi

# Sync dependencies if .venv doesn't exist
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    uv sync --no-install-project
fi

# Run the server
echo "Running server on http://0.0.0.0:8081/mcp"
uv run python main.py