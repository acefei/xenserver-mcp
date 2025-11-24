"""XenServer MCP Server - Model Context Protocol implementation for XenServer administration"""

import logging

from mcp.server.fastmcp import FastMCP

from .config import load_cluster_config
from .prompts import (
    vm_lifecycle_workflow,
    xenserver_mcp_best_practices,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("XenServerMCPServer")


# Create the MCP server (stateless, no connection pooling)
mcp = FastMCP("XenServerMCP")


@mcp.tool()
def list_clusters() -> str:
    """
    List all available XenServer clusters from configuration.
    Shows cluster IDs and their host addresses.
    """
    try:
        config = load_cluster_config()
        if not config:
            return "No clusters configured. Please create a configuration file."

        output = "Available XenServer Clusters:\n\n"
        for cluster_id, cred in config.items():
            output += f"- {cluster_id}\n"
            output += f"  Host: {cred['host']}\n"
            output += f"  User: {cred['username']}\n\n"

        return output
    except Exception as e:
        logger.error(f"Error listing clusters: {str(e)}")
        return f"Error listing clusters: {str(e)}"


@mcp.prompt()
def xenserver_best_practices() -> str:
    """Best practices for XenServer management using MCP"""
    return xenserver_mcp_best_practices()


@mcp.prompt()
def vm_lifecycle() -> str:
    """VM Lifecycle Management Workflow guide"""
    return vm_lifecycle_workflow()


def main():
    """Main entry point for the XenServer MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
