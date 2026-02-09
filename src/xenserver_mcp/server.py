"""XenServer MCP Server - Model Context Protocol implementation for XenServer administration"""

import logging

from mcp.server.fastmcp import FastMCP

from .config import load_cluster_config
from .helpers import format_success, resolve_host, resolve_vm
from .prompts import (
    vm_lifecycle_workflow,
    xenserver_mcp_best_practices,
)
from xen_api.Host import Host
from xen_api.session import xapi_session
from xen_api.VM import VM

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


@mcp.tool()
def list_vms(cluster_id: str) -> str:
    """
    List all VMs in the cluster with basic status.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vms = VM.list_vm(session)
            vm_list = []
            for vm in vms:
                try:
                    vm_list.append(
                        {
                            "name": vm.get_name(),
                            "uuid": vm.get_uuid(),
                            "power_state": vm.get_power_state(),
                            "description": vm.get_description(),
                        }
                    )
                except Exception:
                    continue

            return format_success(vm_list, f"Found {len(vm_list)} VMs in {cluster_id}")
    except Exception as e:
        logger.error(f"Error listing VMs: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_vm_info(cluster_id: str, vm_identifier: str) -> str:
    """
    Get detailed information about a specific VM.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            record = vm.get_record()
            return format_success(record, f"VM Info for {vm_identifier}")

    except Exception as e:
        logger.error(f"Error getting VM info: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def list_vm_templates(cluster_id: str) -> str:
    """
    List available VM templates.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            templates = VM.list_templates(session)
            template_list = []
            for tmpl in templates:
                try:
                    template_list.append(
                        {
                            "name": tmpl.get_name(),
                            "uuid": tmpl.get_uuid(),
                            "description": tmpl.get_description(),
                        }
                    )
                except Exception:
                    continue

            return format_success(
                template_list, f"Found {len(template_list)} templates"
            )
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def start_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Start a VM.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            await vm.start()
            return f"Success: VM '{vm.get_name()}' started"
    except Exception as e:
        logger.error(f"Error starting VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def shutdown_vm(cluster_id: str, vm_identifier: str, force: bool = False) -> str:
    """
    Shutdown a VM (clean or force).
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            if force:
                await vm.force_shutdown()
                return f"Success: VM '{vm.get_name()}' force shutdown"
            else:
                await vm.shutdown()
                return f"Success: VM '{vm.get_name()}' clean shutdown"
    except Exception as e:
        logger.error(f"Error shutting down VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def reboot_vm(cluster_id: str, vm_identifier: str, force: bool = False) -> str:
    """
    Reboot a VM (clean or force).
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            if force:
                await vm.force_reboot()
                return f"Success: VM '{vm.get_name()}' force rebooted"
            else:
                await vm.reboot()
                return f"Success: VM '{vm.get_name()}' clean rebooted"
    except Exception as e:
        logger.error(f"Error rebooting VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def suspend_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Suspend a VM.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            await vm.suspend()
            return f"Success: VM '{vm.get_name()}' suspended"
    except Exception as e:
        logger.error(f"Error suspending VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def resume_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Resume a suspended VM.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            await vm.resume()
            return f"Success: VM '{vm.get_name()}' resumed"
    except Exception as e:
        logger.error(f"Error resuming VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def pause_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Pause a VM.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            await vm.pause()
            return f"Success: VM '{vm.get_name()}' paused"
    except Exception as e:
        logger.error(f"Error pausing VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def unpause_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Unpause a VM.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return f"Error: VM '{vm_identifier}' not found"

            await vm.unpause()
            return f"Success: VM '{vm.get_name()}' unpaused"
    except Exception as e:
        logger.error(f"Error unpausing VM: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def list_hosts(cluster_id: str) -> str:
    """
    List all hosts in the cluster.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            hosts = Host.list_host(session)
            host_list = []
            for host in hosts:
                try:
                    host_list.append(
                        {
                            "name": host.get_name(),
                            "uuid": host.get_uuid(),
                            "address": host.get_address(),
                            "enabled": host.get_enabled(),
                            "description": host.get_description(),
                        }
                    )
                except Exception:
                    continue

            return format_success(
                host_list, f"Found {len(host_list)} hosts in {cluster_id}"
            )
    except Exception as e:
        logger.error(f"Error listing hosts: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_host_info(cluster_id: str, host_identifier: str) -> str:
    """
    Get detailed information about a specific host.
    """
    try:
        config = load_cluster_config()
        if cluster_id not in config:
            return f"Error: Cluster '{cluster_id}' not found"

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return f"Error: Host '{host_identifier}' not found"

            # Use serialize method or get_record
            # serialize() provides a cleaner view
            return format_success(host.serialize(), f"Host Info for {host_identifier}")

    except Exception as e:
        logger.error(f"Error getting host info: {str(e)}")
        return f"Error: {str(e)}"


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
