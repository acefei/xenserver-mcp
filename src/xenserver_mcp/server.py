"""XenServer MCP Server - Model Context Protocol implementation for XenServer administration"""

import logging

from mcp.server.fastmcp import FastMCP

from .config import load_cluster_config
from .helpers import (
    format_error,
    format_success,
    resolve_host,
    resolve_network,
    resolve_sr,
    resolve_vdi,
    resolve_vm,
    retry_async,
    retry_sync,
    validate_cluster_id,
    validate_non_empty_list,
    validate_positive_int,
    validate_required,
)
from .prompts import (
    host_maintenance_workflow,
    network_management_workflow,
    storage_management_workflow,
    vm_lifecycle_workflow,
    xenserver_mcp_best_practices,
)
from xen_api.Host import Host
from xen_api.Network import Network
from xen_api.PIF import PIF
from xen_api.session import xapi_session
from xen_api.SR import SR
from xen_api.VBD import VBD
from xen_api.VDI import VDI
from xen_api.VIF import VIF
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
            return format_error(
                "No clusters configured. Please create a configuration file.",
                code="no_clusters",
            )

        output = "Available XenServer Clusters:\n\n"
        for cluster_id, cred in config.items():
            output += f"- {cluster_id}\n"
            output += f"  Host: {cred['host']}\n"
            output += f"  User: {cred['username']}\n\n"

        return output
    except Exception as e:
        logger.error(f"Error listing clusters: {str(e)}")
        return format_error(
            f"Failed to list clusters: {str(e)}", code="operation_failed"
        )


@mcp.tool()
def list_vms(cluster_id: str) -> str:
    """
    List all VMs in the cluster with basic status.

    Args:
        cluster_id: The identifier of the cluster to query.

    Returns:
        A formatted string containing a list of VMs with their name, UUID, power state, and description.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

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
        return format_error(f"Failed to list VMs: {str(e)}", code="operation_failed")


@mcp.tool()
def get_vm_info(cluster_id: str, vm_identifier: str) -> str:
    """
    Get detailed information about a specific VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        A formatted string containing detailed VM record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            record = vm.get_record()
            return format_success(record, f"VM Info for {vm_identifier}")

    except Exception as e:
        logger.error(f"Error getting VM info: {str(e)}")
        return format_error(f"Failed to get VM info: {str(e)}", code="operation_failed")


@mcp.tool()
def list_vm_templates(cluster_id: str) -> str:
    """
    List available VM templates.

    Args:
        cluster_id: The identifier of the cluster.

    Returns:
        A formatted string containing a list of templates with their name, UUID, and description.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

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
        return format_error(
            f"Failed to list templates: {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def start_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Start a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to start.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            vm_id = vm.get_uuid()
            await retry_async(lambda: vm.start())
            return f"Success: VM '{vm_name}' started"
    except Exception as e:
        logger.error(f"Error starting VM: {str(e)}")
        return format_error(
            f"Error starting VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def shutdown_vm(cluster_id: str, vm_identifier: str, force: bool = False) -> str:
    """
    Shutdown a VM (clean or force).

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to shutdown.
        force: If True, performs a hard shutdown. If False, performs a clean shutdown.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            if force:
                await retry_async(lambda: vm.force_shutdown())
                return f"Success: VM '{vm_name}' force shutdown"
            else:
                await retry_async(lambda: vm.shutdown())
                return f"Success: VM '{vm_name}' clean shutdown"
    except Exception as e:
        logger.error(f"Error shutting down VM: {str(e)}")
        return format_error(
            f"Error shutting down VM '{vm_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
async def reboot_vm(cluster_id: str, vm_identifier: str, force: bool = False) -> str:
    """
    Reboot a VM (clean or force).

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to reboot.
        force: If True, performs a hard reboot. If False, performs a clean reboot.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            if force:
                await retry_async(lambda: vm.force_reboot())
                return f"Success: VM '{vm_name}' force rebooted"
            else:
                await retry_async(lambda: vm.reboot())
                return f"Success: VM '{vm_name}' clean rebooted"
    except Exception as e:
        logger.error(f"Error rebooting VM: {str(e)}")
        return format_error(
            f"Error rebooting VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def suspend_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Suspend a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to suspend.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.suspend())
            return f"Success: VM '{vm_name}' suspended"
    except Exception as e:
        logger.error(f"Error suspending VM: {str(e)}")
        return format_error(
            f"Error suspending VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def resume_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Resume a suspended VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to resume.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.resume())
            return f"Success: VM '{vm_name}' resumed"
    except Exception as e:
        logger.error(f"Error resuming VM: {str(e)}")
        return format_error(
            f"Error resuming VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def pause_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Pause a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to pause.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.pause())
            return f"Success: VM '{vm_name}' paused"
    except Exception as e:
        logger.error(f"Error pausing VM: {str(e)}")
        return format_error(
            f"Error pausing VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def unpause_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Unpause a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to unpause.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.unpause())
            return f"Success: VM '{vm_name}' unpaused"
    except Exception as e:
        logger.error(f"Error unpausing VM: {str(e)}")
        return format_error(
            f"Error unpause VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def batch_start_vms(cluster_id: str, vm_identifiers: list[str]) -> str:
    """
    Start multiple VMs in sequence.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifiers: A list of VM names or UUIDs to start.

    Returns:
        A summary of successful and failed operations.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_non_empty_list(vm_identifiers, "vm_identifiers")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            successes = []
            failures = []

            for vm_identifier in vm_identifiers:
                try:
                    vm = resolve_vm(session, vm_identifier)
                    if not vm:
                        failures.append(
                            {
                                "identifier": vm_identifier,
                                "error": f"VM '{vm_identifier}' not found",
                            }
                        )
                        continue

                    vm_name = vm.get_name()
                    await vm.start()
                    successes.append(
                        {
                            "identifier": vm_identifier,
                            "name": vm_name,
                            "status": "started",
                        }
                    )
                except Exception as e:
                    failures.append(
                        {
                            "identifier": vm_identifier,
                            "error": str(e),
                        }
                    )

            result = {
                "total": len(vm_identifiers),
                "successful": len(successes),
                "failed": len(failures),
                "successes": successes,
                "failures": failures,
            }

            summary = f"Batch start completed: {len(successes)} succeeded, {len(failures)} failed"
            return format_success(result, summary)

    except Exception as e:
        logger.error(f"Error in batch start VMs: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
async def batch_shutdown_vms(cluster_id: str, vm_identifiers: list[str]) -> str:
    """
    Shutdown multiple VMs in sequence (clean shutdown).

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifiers: A list of VM names or UUIDs to shutdown.

    Returns:
        A summary of successful and failed operations.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_non_empty_list(vm_identifiers, "vm_identifiers")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            successes = []
            failures = []

            for vm_identifier in vm_identifiers:
                try:
                    vm = resolve_vm(session, vm_identifier)
                    if not vm:
                        failures.append(
                            {
                                "identifier": vm_identifier,
                                "error": f"VM '{vm_identifier}' not found",
                            }
                        )
                        continue

                    vm_name = vm.get_name()
                    await vm.shutdown()
                    successes.append(
                        {
                            "identifier": vm_identifier,
                            "name": vm_name,
                            "status": "shutdown",
                        }
                    )
                except Exception as e:
                    failures.append(
                        {
                            "identifier": vm_identifier,
                            "error": str(e),
                        }
                    )

            result = {
                "total": len(vm_identifiers),
                "successful": len(successes),
                "failed": len(failures),
                "successes": successes,
                "failures": failures,
            }

            summary = f"Batch shutdown completed: {len(successes)} succeeded, {len(failures)} failed"
            return format_success(result, summary)

    except Exception as e:
        logger.error(f"Error in batch shutdown VMs: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
async def create_vm_snapshot(
    cluster_id: str, vm_identifier: str, snapshot_name: str
) -> str:
    """
    Create a snapshot of a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to snapshot.
        snapshot_name: The name to give the new snapshot.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        error = validate_required(snapshot_name, "snapshot_name")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.snapshot(snapshot_name))
            return f"Success: Snapshot '{snapshot_name}' created for VM '{vm_name}'"
    except Exception as e:
        logger.error(f"Error creating snapshot: {str(e)}")
        return format_error(
            f"Error creating snapshot for VM '{vm_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def list_vm_snapshots(cluster_id: str, vm_identifier: str) -> str:
    """
    List all snapshots for a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        A formatted string containing a list of snapshots with their name, UUID, time, and description.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            snapshots = vm.get_snapshots()
            snapshot_list = []
            for snap in snapshots:
                try:
                    snapshot_list.append(
                        {
                            "name": snap.get_name(),
                            "uuid": snap.get_uuid(),
                            "snapshot_time": snap.get_snapshot_time(),
                            "description": snap.get_description(),
                        }
                    )
                except Exception:
                    continue

            return format_success(
                snapshot_list,
                f"Found {len(snapshot_list)} snapshots for VM '{vm.get_name()}'",
            )
    except Exception as e:
        logger.error(f"Error listing snapshots: {str(e)}")
        return format_error(
            f"Error listing snapshots for VM '{vm_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
async def delete_vm_snapshot(cluster_id: str, snapshot_identifier: str) -> str:
    """
    Delete a VM snapshot by UUID or name.

    Args:
        cluster_id: The identifier of the cluster.
        snapshot_identifier: The name or UUID of the snapshot to delete.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(snapshot_identifier, "snapshot_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            snapshot = resolve_vm(session, snapshot_identifier)
            if not snapshot:
                return format_error(
                    f"Snapshot '{snapshot_identifier}' not found",
                    code="resource_not_found",
                )

            snapshot_name = snapshot.get_name()
            await retry_async(lambda: snapshot.destroy())
            return f"Success: Snapshot '{snapshot_name}' deleted"
    except Exception as e:
        logger.error(f"Error deleting snapshot: {str(e)}")
        return format_error(
            f"Error deleting snapshot '{snapshot_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
async def clone_vm(cluster_id: str, vm_identifier: str, new_name: str) -> str:
    """
    Clone a VM to create a new VM with the same configuration.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the source VM.
        new_name: The name for the new cloned VM.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        error = validate_required(new_name, "new_name")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.clone(new_name))
            return f"Success: VM '{vm_name}' cloned to '{new_name}'"
    except Exception as e:
        logger.error(f"Error cloning VM: {str(e)}")
        return format_error(
            f"Error cloning VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def copy_vm(
    cluster_id: str, vm_identifier: str, new_name: str, sr_identifier: str
) -> str:
    """
    Copy a VM to a different storage repository.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the source VM.
        new_name: The name for the new copied VM.
        sr_identifier: The name or UUID of the destination storage repository.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        error = validate_required(new_name, "new_name")
        if error:
            return error

        error = validate_required(sr_identifier, "sr_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            sr = resolve_sr(session, sr_identifier)
            if not sr:
                return format_error(
                    f"SR '{sr_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            sr_name = sr.get_name()
            await retry_async(lambda: vm.copy(new_name, sr))
            return f"Success: VM '{vm_name}' copied to '{new_name}' on SR '{sr_name}'"
    except Exception as e:
        logger.error(f"Error copying VM: {str(e)}")
        return format_error(
            f"Error copying VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def delete_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Delete a VM and its associated disks.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM to delete.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.delete())
            return f"Success: VM '{vm_name}' deleted"
    except Exception as e:
        logger.error(f"Error deleting VM: {str(e)}")
        return format_error(
            f"Error deleting VM '{vm_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def provision_vm(cluster_id: str, vm_identifier: str) -> str:
    """
    Provision a VM from a template (converts template to a working VM).

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the template to provision.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            await retry_async(lambda: vm.provision())
            return f"Success: VM '{vm_name}' provisioned"
    except Exception as e:
        logger.error(f"Error provisioning VM: {str(e)}")
        return format_error(
            f"Error provisioning VM '{vm_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def set_vm_vcpus(
    cluster_id: str, vm_identifier: str, vcpus: int, sockets: int = 1
) -> str:
    """
    Set the number of vCPUs for a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.
        vcpus: The total number of vCPUs.
        sockets: The number of CPU sockets (default: 1).

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        error = validate_positive_int(vcpus, "vcpus")
        if error:
            return error

        error = validate_positive_int(sockets, "sockets")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            vm.set_vCPUs(vcpus, sockets)
            return f"Success: VM '{vm_name}' vCPUs set to {vcpus} (sockets: {sockets})"
    except Exception as e:
        logger.error(f"Error setting VM vCPUs: {str(e)}")
        return format_error(
            f"Error setting vCPUs for VM '{vm_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def set_vm_memory(cluster_id: str, vm_identifier: str, memory_bytes: int) -> str:
    """
    Set the memory for a VM in bytes.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.
        memory_bytes: The memory size in bytes.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vm_identifier, "vm_identifier")
        if error:
            return error

        error = validate_positive_int(memory_bytes, "memory_bytes")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vm_name = vm.get_name()
            vm.set_memory(memory_bytes)
            memory_gb = memory_bytes / (1024**3)
            return f"Success: VM '{vm_name}' memory set to {memory_bytes} bytes ({memory_gb:.2f} GB)"
    except Exception as e:
        logger.error(f"Error setting VM memory: {str(e)}")
        return format_error(
            f"Error setting memory for VM '{vm_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def get_vm_guest_metrics(cluster_id: str, vm_identifier: str) -> str:
    """
    Get guest OS metrics for a VM (requires guest tools to be installed).

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        A formatted string containing guest metrics (OS version, networks, etc.).
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            guest_metrics = vm.get_guest_metrics()
            if not guest_metrics:
                return format_error(
                    f"Guest metrics not available for VM '{vm.get_name()}'. Guest tools may not be installed or the VM may not be running.",
                    code="metrics_unavailable",
                )

            metrics_data = guest_metrics.serialize()
            return format_success(
                metrics_data, f"Guest metrics for VM '{vm.get_name()}'"
            )

    except Exception as e:
        logger.error(f"Error getting VM guest metrics: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_vm_console_url(cluster_id: str, vm_identifier: str) -> str:
    """
    Get console access information for a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        Console access information (currently returns not implemented).
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            return format_error(
                f"Console URL functionality is not yet implemented in the XenAPI wrapper. VM '{vm.get_name()}' found, but console access requires additional implementation.",
                code="not_implemented",
            )

    except Exception as e:
        logger.error(f"Error getting VM console URL: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def list_vm_disks(cluster_id: str, vm_identifier: str) -> str:
    """
    List all disks (VBDs) attached to a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        A formatted string containing a list of attached disks with their VBD and VDI details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vbds = vm.get_VBDs()
            disk_list = []
            for vbd in vbds:
                try:
                    vdi = vbd.get_VDI()
                    disk_info = {
                        "vbd_uuid": vbd.get_uuid(),
                        "device": vbd.get_device(),
                        "type": vbd.get_type(),
                        "mode": vbd.get_mode(),
                        "bootable": vbd.get_bootable(),
                        "attached": vbd.get_currently_attached(),
                        "unpluggable": vbd.get_unpluggable(),
                    }

                    if vdi:
                        disk_info["vdi_uuid"] = vdi.get_uuid()
                        disk_info["vdi_name"] = vdi.get_name()
                        disk_info["vdi_size"] = vdi.get_virtual_size()
                        disk_info["vdi_type"] = vdi.get_type()
                    else:
                        disk_info["vdi_uuid"] = None
                        disk_info["vdi_name"] = "Empty"

                    disk_list.append(disk_info)
                except Exception:
                    continue

            return format_success(
                disk_list, f"Found {len(disk_list)} disk(s) for VM '{vm.get_name()}'"
            )
    except Exception as e:
        logger.error(f"Error listing VM disks: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def attach_disk_to_vm(
    cluster_id: str, vm_identifier: str, vdi_identifier: str, bootable: bool = False
) -> str:
    """
    Attach an existing VDI to a VM as a disk.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.
        vdi_identifier: The name or UUID of the VDI to attach.
        bootable: Whether the disk should be bootable (default: False).

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vdi = resolve_vdi(session, vdi_identifier)
            if not vdi:
                return format_error(
                    f"VDI '{vdi_identifier}' not found", code="resource_not_found"
                )

            # Find next available device number
            existing_vbds = vm.get_VBDs()
            used_devices = []
            for vbd in existing_vbds:
                try:
                    device = vbd.get_device()
                    if device.isdigit():
                        used_devices.append(int(device))
                except Exception:
                    continue

            next_device = 0
            while next_device in used_devices:
                next_device += 1

            # Create and plug VBD
            vbd = VBD.create(
                session,
                vm,
                vdi,
                userdevice=str(next_device),
                bootable=bootable,
                mode="RW",
                disk_type="Disk",
            )

            # Hot-plug if VM is running
            power_state = vm.get_power_state()
            if power_state == "Running":
                vbd.plug()

            return f"Success: VDI '{vdi.get_name()}' attached to VM '{vm.get_name()}' as device {next_device}"
    except Exception as e:
        logger.error(f"Error attaching disk to VM: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def detach_disk_from_vm(cluster_id: str, vbd_identifier: str) -> str:
    """
    Detach a disk from a VM by VBD UUID.

    Args:
        cluster_id: The identifier of the cluster.
        vbd_identifier: The UUID of the VBD (Virtual Block Device) to detach.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vbd = VBD.get_by_uuid(session, vbd_identifier)
            if not vbd:
                return format_error(
                    f"VBD '{vbd_identifier}' not found", code="resource_not_found"
                )

            vm = vbd.get_VM()
            vdi = vbd.get_VDI()

            vm_name = vm.get_name() if vm else "Unknown"
            vdi_name = vdi.get_name() if vdi else "Unknown"

            # Unplug if currently attached
            if vbd.get_currently_attached():
                vbd.unplug()

            # Destroy VBD
            vbd.destroy()

            return f"Success: Disk '{vdi_name}' detached from VM '{vm_name}'"
    except Exception as e:
        logger.error(f"Error detaching disk from VM: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def mount_iso(cluster_id: str, vm_identifier: str, vdi_identifier: str) -> str:
    """
    Mount an ISO VDI to a VM's CD drive.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.
        vdi_identifier: The name or UUID of the ISO VDI.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vdi = resolve_vdi(session, vdi_identifier)
            if not vdi:
                return format_error(
                    f"VDI '{vdi_identifier}' not found", code="resource_not_found"
                )

            # Check if VDI is an ISO
            if vdi.get_type() not in ["User", "System"]:
                return format_error(
                    f"VDI '{vdi_identifier}' is not a valid ISO type (type: {vdi.get_type()})",
                    code="validation_error",
                )

            # Get existing CD drives
            cd_vbds = vm.get_CDs()

            if not cd_vbds:
                # No CD drive exists, create one
                vbd = VBD.create(
                    session,
                    vm,
                    vdi,
                    userdevice="3",  # Standard CD device number
                    bootable=False,
                    mode="RO",
                    disk_type="CD",
                    empty=False,
                )

                # Hot-plug if VM is running
                power_state = vm.get_power_state()
                if power_state == "Running":
                    vbd.plug()

                return (
                    f"Success: ISO '{vdi.get_name()}' mounted to VM '{vm.get_name()}'"
                )
            else:
                # Use existing CD drive
                cd_vbd = cd_vbds[0]

                # Eject if something is already mounted
                existing_vdi = cd_vbd.get_VDI()
                if existing_vdi:
                    cd_vbd.eject()

                # Insert new ISO
                cd_vbd.insert(vdi)

                return (
                    f"Success: ISO '{vdi.get_name()}' mounted to VM '{vm.get_name()}'"
                )
    except Exception as e:
        logger.error(f"Error mounting ISO: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def eject_iso(cluster_id: str, vm_identifier: str) -> str:
    """
    Eject ISO from a VM's CD drive.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            # Get CD drives
            cd_vbds = vm.get_CDs()

            if not cd_vbds:
                return format_error(
                    f"VM '{vm.get_name()}' has no CD drive", code="resource_not_found"
                )

            # Eject from first CD drive
            cd_vbd = cd_vbds[0]
            existing_vdi = cd_vbd.get_VDI()

            if not existing_vdi:
                return f"Success: No ISO mounted in VM '{vm.get_name()}' CD drive"

            vdi_name = existing_vdi.get_name()
            cd_vbd.eject()

            return f"Success: ISO '{vdi_name}' ejected from VM '{vm.get_name()}'"
    except Exception as e:
        logger.error(f"Error ejecting ISO: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def list_hosts(cluster_id: str) -> str:
    """
    List all hosts in the cluster.

    Args:
        cluster_id: The identifier of the cluster.

    Returns:
        A formatted string containing a list of hosts with their name, UUID, address, and status.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            hosts = Host.list_host(session)
            host_list = []
            for host in hosts:
                try:
                    host_record = host.get_record()
                    host_list.append(
                        {
                            "name": host_record.get("name_label", host.get_name()),
                            "uuid": host_record.get("uuid", host.get_uuid()),
                            "address": host_record.get("address", host.get_address()),
                            "enabled": host_record.get("enabled", host.get_enabled()),
                            "description": host_record.get("name_description"),
                        }
                    )
                except Exception:
                    continue

            return format_success(
                host_list, f"Found {len(host_list)} hosts in {cluster_id}"
            )
    except Exception as e:
        logger.error(f"Error listing hosts: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_host_info(cluster_id: str, host_identifier: str) -> str:
    """
    Get detailed information about a specific host.

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: The name or UUID of the host.

    Returns:
        A formatted string containing detailed host record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return format_error(
                    f"Host '{host_identifier}' not found", code="resource_not_found"
                )

            # Use serialize method or get_record
            # serialize() provides a cleaner view
            return format_success(host.serialize(), f"Host Info for {host_identifier}")

    except Exception as e:
        logger.error(f"Error getting host info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_host_metrics(cluster_id: str, host_identifier: str) -> str:
    """
    Get host CPU and memory metrics.

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: The name or UUID of the host.

    Returns:
        A formatted string containing host metrics (free/total memory, CPU info).
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return format_error(
                    f"Host '{host_identifier}' not found", code="resource_not_found"
                )

            # Gather metrics
            metrics_data = {
                "host_name": host.get_name(),
                "host_uuid": host.get_uuid(),
                "free_memory_bytes": host.get_free_memory(),
                "total_memory_bytes": host.get_total_memory(),
                "cpu_info": host.get_cpu_info(),
            }

            return format_success(metrics_data, f"Host metrics for {host.get_name()}")

    except Exception as e:
        logger.error(f"Error getting host metrics: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_host_capabilities(cluster_id: str, host_identifier: str) -> str:
    """
    Get host capabilities.

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: The name or UUID of the host.

    Returns:
        A formatted string containing host capabilities.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return format_error(
                    f"Host '{host_identifier}' not found", code="resource_not_found"
                )

            # Get capabilities
            capabilities = host.get_capabilities()

            capabilities_data = {
                "host_name": host.get_name(),
                "host_uuid": host.get_uuid(),
                "capabilities": capabilities,
            }

            return format_success(
                capabilities_data, f"Host capabilities for {host.get_name()}"
            )

    except Exception as e:
        logger.error(f"Error getting host capabilities: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def enable_host(cluster_id: str, host_identifier: str) -> str:
    """
    Enable a host (allows new VMs to be placed on it).

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: The name or UUID of the host to enable.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(host_identifier, "host_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return format_error(
                    f"Host '{host_identifier}' not found", code="resource_not_found"
                )

            host_name = host.get_name()
            retry_sync(lambda: host.enable())
            return f"Success: Host '{host_name}' enabled"

    except Exception as e:
        logger.error(f"Error enabling host: {str(e)}")
        return format_error(
            f"Error enabling host '{host_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def disable_host(cluster_id: str, host_identifier: str) -> str:
    """
    Disable a host (prevents new VMs from being placed on it).

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: The name or UUID of the host to disable.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(host_identifier, "host_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return format_error(
                    f"Host '{host_identifier}' not found", code="resource_not_found"
                )

            host_name = host.get_name()
            retry_sync(lambda: host.disable())
            return f"Success: Host '{host_name}' disabled"

    except Exception as e:
        logger.error(f"Error disabling host: {str(e)}")
        return format_error(
            f"Error disabling host '{host_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def evacuate_host(cluster_id: str, host_identifier: str) -> str:
    """
    Evacuate all VMs from a host (migrates VMs to other hosts in the pool).

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: The name or UUID of the host to evacuate.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(host_identifier, "host_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            host = resolve_host(session, host_identifier)
            if not host:
                return format_error(
                    f"Host '{host_identifier}' not found", code="resource_not_found"
                )

            host_name = host.get_name()
            retry_sync(lambda: host.evacuate())
            return f"Success: Host '{host_name}' evacuated - all VMs migrated to other hosts"

    except Exception as e:
        logger.error(f"Error evacuating host: {str(e)}")
        return format_error(
            f"Error evacuating host '{host_identifier}': {str(e)}",
            code="operation_failed",
        )


@mcp.tool()
def list_storage_repositories(cluster_id: str) -> str:
    """
    List all storage repositories (SRs) in the cluster.

    Args:
        cluster_id: The identifier of the cluster.

    Returns:
        A formatted string containing a list of SRs with their name, UUID, type, and capacity.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            srs = SR.get_all(session)
            sr_list = []
            for sr in srs:
                try:
                    sr_data = sr.serialize()
                    sr_list.append(sr_data)
                except Exception:
                    continue

            return format_success(
                sr_list, f"Found {len(sr_list)} storage repositories in {cluster_id}"
            )
    except Exception as e:
        logger.error(f"Error listing storage repositories: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_sr_info(cluster_id: str, sr_identifier: str) -> str:
    """
    Get detailed information about a specific storage repository including VDIs.

    Args:
        cluster_id: The identifier of the cluster.
        sr_identifier: The name or UUID of the storage repository.

    Returns:
        A formatted string containing detailed SR record information and a list of VDIs.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            sr = resolve_sr(session, sr_identifier)
            if not sr:
                return format_error(
                    f"SR '{sr_identifier}' not found", code="resource_not_found"
                )

            # Get SR information
            sr_data = sr.serialize()

            # Get VDIs in the SR
            try:
                vdis = sr.get_VDIs()
                vdi_list = []
                for vdi in vdis:
                    try:
                        vdi_record = vdi.get_record()
                        vdi_list.append(
                            {
                                "uuid": vdi_record.get("uuid", vdi.get_uuid()),
                                "name": vdi_record.get("name_label", vdi.get_name()),
                                "virtual_size": vdi_record.get("virtual_size"),
                                "physical_utilisation": vdi_record.get(
                                    "physical_utilisation"
                                ),
                                "type": vdi_record.get("type"),
                                "sharable": vdi_record.get("sharable"),
                                "read_only": vdi_record.get("read_only"),
                            }
                        )
                    except Exception:
                        continue

                sr_data["vdis"] = vdi_list
                sr_data["vdi_count"] = len(vdi_list)
            except Exception as e:
                logger.warning(f"Could not retrieve VDIs for SR: {str(e)}")
                sr_data["vdis"] = []
                sr_data["vdi_count"] = 0

            return format_success(sr_data, f"SR Info for {sr_identifier}")

    except Exception as e:
        logger.error(f"Error getting SR info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def scan_sr(cluster_id: str, sr_identifier: str) -> str:
    """
    Scan a storage repository for changes (useful for detecting new VDIs or LUNs).

    Args:
        cluster_id: The identifier of the cluster.
        sr_identifier: The name or UUID of the storage repository to scan.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(sr_identifier, "sr_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            sr = resolve_sr(session, sr_identifier)
            if not sr:
                return format_error(
                    f"SR '{sr_identifier}' not found", code="resource_not_found"
                )

            sr_name = sr.get_name()
            retry_sync(lambda: sr.scan())
            return f"Success: SR '{sr_name}' scanned successfully"

    except Exception as e:
        logger.error(f"Error scanning SR: {str(e)}")
        return format_error(
            f"Error scanning SR '{sr_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
def list_vdis(cluster_id: str, sr_identifier: str | None = None) -> str:
    """
    List VDIs (Virtual Disk Images), optionally filtered by SR.

    Args:
        cluster_id: The identifier of the cluster.
        sr_identifier: Optional name or UUID of an SR to filter VDIs.

    Returns:
        A formatted string containing a list of VDIs with their name, UUID, type, and size.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            if sr_identifier:
                # Filter by SR
                sr = resolve_sr(session, sr_identifier)
                if not sr:
                    return format_error(
                        f"SR '{sr_identifier}' not found", code="resource_not_found"
                    )

                vdis = sr.get_VDIs()
                location_msg = f" in SR '{sr.get_name()}'"
            else:
                # Get all VDIs
                vdis = VDI.get_all(session)
                location_msg = ""

            vdi_list = []
            for vdi in vdis:
                try:
                    vdi_list.append(
                        {
                            "name": vdi.get_name(),
                            "uuid": vdi.get_uuid(),
                            "type": vdi.get_type(),
                            "virtual_size": vdi.get_virtual_size(),
                            "description": vdi.get_description(),
                        }
                    )
                except Exception:
                    continue

            return format_success(
                vdi_list, f"Found {len(vdi_list)} VDI(s){location_msg}"
            )
    except Exception as e:
        logger.error(f"Error listing VDIs: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_vdi_info(cluster_id: str, vdi_identifier: str) -> str:
    """
    Get detailed information about a specific VDI.

    Args:
        cluster_id: The identifier of the cluster.
        vdi_identifier: The name or UUID of the VDI.

    Returns:
        A formatted string containing detailed VDI record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vdi = resolve_vdi(session, vdi_identifier)
            if not vdi:
                return format_error(
                    f"VDI '{vdi_identifier}' not found", code="resource_not_found"
                )

            # Get serialized data plus additional record fields
            vdi_data = vdi.serialize()

            # Add additional useful fields from record
            try:
                record = vdi.get_record()
                vdi_data["virtual_size"] = record.get("virtual_size")
                vdi_data["physical_utilisation"] = record.get("physical_utilisation")
                vdi_data["sharable"] = record.get("sharable")
                vdi_data["read_only"] = record.get("read_only")
                vdi_data["storage_lock"] = record.get("storage_lock")
                vdi_data["managed"] = record.get("managed")

                # Get SR name
                sr = vdi.get_SR()
                if sr:
                    vdi_data["sr_name"] = sr.get_name()
                    vdi_data["sr_uuid"] = sr.get_uuid()
            except Exception as e:
                logger.warning(f"Could not retrieve additional VDI fields: {str(e)}")

            return format_success(vdi_data, f"VDI Info for {vdi_identifier}")

    except Exception as e:
        logger.error(f"Error getting VDI info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
async def resize_vdi(cluster_id: str, vdi_identifier: str, new_size_bytes: int) -> str:
    """
    Resize a VDI to a new size in bytes.

    Args:
        cluster_id: The identifier of the cluster.
        vdi_identifier: The name or UUID of the VDI to resize.
        new_size_bytes: The new size for the VDI in bytes.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vdi_identifier, "vdi_identifier")
        if error:
            return error

        error = validate_positive_int(new_size_bytes, "new_size_bytes")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vdi = resolve_vdi(session, vdi_identifier)
            if not vdi:
                return format_error(
                    f"VDI '{vdi_identifier}' not found", code="resource_not_found"
                )

            vdi_name = vdi.get_name()
            old_size = vdi.get_virtual_size()

            # Convert int to string as expected by the API
            await retry_async(lambda: vdi.resize(str(new_size_bytes)))

            size_gb = new_size_bytes / (1024**3)
            return f"Success: VDI '{vdi_name}' resized from {old_size} to {new_size_bytes} bytes ({size_gb:.2f} GB)"
    except Exception as e:
        logger.error(f"Error resizing VDI: {str(e)}")
        return format_error(
            f"Error resizing VDI '{vdi_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
async def clone_vdi(cluster_id: str, vdi_identifier: str) -> str:
    """
    Clone a VDI to create a new copy.

    Args:
        cluster_id: The identifier of the cluster.
        vdi_identifier: The name or UUID of the VDI to clone.

    Returns:
        A success message with the new VDI UUID or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vdi_identifier, "vdi_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vdi = resolve_vdi(session, vdi_identifier)
            if not vdi:
                return format_error(
                    f"VDI '{vdi_identifier}' not found", code="resource_not_found"
                )

            vdi_name = vdi.get_name()
            cloned_vdi = await retry_async(lambda: vdi.clone())

            return f"Success: VDI '{vdi_name}' cloned to new VDI with UUID '{cloned_vdi.get_uuid()}'"
    except Exception as e:
        logger.error(f"Error cloning VDI: {str(e)}")
        return format_error(
            f"Error cloning VDI '{vdi_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
def delete_vdi(cluster_id: str, vdi_identifier: str) -> str:
    """
    Delete a VDI (Virtual Disk Image).

    Args:
        cluster_id: The identifier of the cluster.
        vdi_identifier: The name or UUID of the VDI to delete.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        error = validate_required(vdi_identifier, "vdi_identifier")
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vdi = resolve_vdi(session, vdi_identifier)
            if not vdi:
                return format_error(
                    f"VDI '{vdi_identifier}' not found", code="resource_not_found"
                )

            vdi_name = vdi.get_name()
            retry_sync(lambda: vdi.destroy())

            return f"Success: VDI '{vdi_name}' deleted"
    except Exception as e:
        logger.error(f"Error deleting VDI: {str(e)}")
        return format_error(
            f"Error deleting VDI '{vdi_identifier}': {str(e)}", code="operation_failed"
        )


@mcp.tool()
def list_networks(cluster_id: str) -> str:
    """
    List all virtual networks in the cluster.

    Args:
        cluster_id: The identifier of the cluster.

    Returns:
        A formatted string containing a list of networks with their name, UUID, description, and MTU.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            networks = Network.get_all(session)
            network_list = []
            for network in networks:
                try:
                    network_list.append(
                        {
                            "uuid": network.get_uuid(),
                            "name": network.get_name(),
                            "description": network.get_description(),
                            "mtu": network.get_mtu(),
                        }
                    )
                except Exception:
                    continue

            return format_success(
                network_list, f"Found {len(network_list)} network(s) in {cluster_id}"
            )
    except Exception as e:
        logger.error(f"Error listing networks: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_network_info(cluster_id: str, network_identifier: str) -> str:
    """
    Get detailed information about a specific network.

    Args:
        cluster_id: The identifier of the cluster.
        network_identifier: The name or UUID of the network.

    Returns:
        A formatted string containing detailed network record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            network = resolve_network(session, network_identifier)
            if not network:
                return format_error(
                    f"Network '{network_identifier}' not found",
                    code="resource_not_found",
                )

            network_data = {
                "uuid": network.get_uuid(),
                "name": network.get_name(),
                "description": network.get_description(),
                "mtu": network.get_mtu(),
            }

            return format_success(
                network_data, f"Network Info for {network_identifier}"
            )

    except Exception as e:
        logger.error(f"Error getting network info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def list_vm_vifs(cluster_id: str, vm_identifier: str) -> str:
    """
    List all Virtual Interfaces (VIFs) for a VM.

    Args:
        cluster_id: The identifier of the cluster.
        vm_identifier: The name or UUID of the VM.

    Returns:
        A formatted string containing a list of VIFs with their UUID, device, MAC, and network details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vm = resolve_vm(session, vm_identifier)
            if not vm:
                return format_error(
                    f"VM '{vm_identifier}' not found", code="resource_not_found"
                )

            vifs = vm.get_VIFs()
            vif_list = []
            for vif in vifs:
                try:
                    network = vif.get_network()
                    vif_info = {
                        "uuid": vif.get_uuid(),
                        "device": vif.get_device(),
                        "mac": vif.get_mac(),
                        "mtu": vif.get_mtu(),
                        "network_uuid": network.get_uuid(),
                        "network_name": network.get_name(),
                        "attached": vif.get_attached(),
                    }
                    vif_list.append(vif_info)
                except Exception:
                    continue

            return format_success(
                vif_list, f"Found {len(vif_list)} VIF(s) for VM '{vm.get_name()}'"
            )
    except Exception as e:
        logger.error(f"Error listing VM VIFs: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_vif_info(cluster_id: str, vif_identifier: str) -> str:
    """
    Get detailed information about a specific Virtual Interface (VIF).

    Args:
        cluster_id: The identifier of the cluster.
        vif_identifier: The UUID of the VIF.

    Returns:
        A formatted string containing detailed VIF record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vif = VIF.get_by_uuid(session, vif_identifier)
            if not vif:
                return format_error(
                    f"VIF '{vif_identifier}' not found", code="resource_not_found"
                )

            network = vif.get_network()
            vif_data = {
                "uuid": vif.get_uuid(),
                "device": vif.get_device(),
                "mac": vif.get_mac(),
                "mtu": vif.get_mtu(),
                "network_uuid": network.get_uuid(),
                "network_name": network.get_name(),
                "attached": vif.get_attached(),
            }

            return format_success(vif_data, f"VIF Info for {vif_identifier}")

    except Exception as e:
        logger.error(f"Error getting VIF info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def plug_vif(cluster_id: str, vif_identifier: str) -> str:
    """
    Hot-plug a Virtual Interface (VIF) to a running VM.

    Args:
        cluster_id: The identifier of the cluster.
        vif_identifier: The UUID of the VIF to plug.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vif = VIF.get_by_uuid(session, vif_identifier)
            if not vif:
                return format_error(
                    f"VIF '{vif_identifier}' not found", code="resource_not_found"
                )

            # Check if already attached
            if vif.get_attached():
                return f"Success: VIF '{vif.get_uuid()}' is already attached"

            vif.plug()
            return f"Success: VIF '{vif.get_uuid()}' plugged successfully"

    except Exception as e:
        logger.error(f"Error plugging VIF: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def unplug_vif(cluster_id: str, vif_identifier: str) -> str:
    """
    Hot-unplug a Virtual Interface (VIF) from a running VM.

    Args:
        cluster_id: The identifier of the cluster.
        vif_identifier: The UUID of the VIF to unplug.

    Returns:
        A success message or error details.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            vif = VIF.get_by_uuid(session, vif_identifier)
            if not vif:
                return format_error(
                    f"VIF '{vif_identifier}' not found", code="resource_not_found"
                )

            # Check if already detached
            if not vif.get_attached():
                return f"Success: VIF '{vif.get_uuid()}' is already detached"

            vif.unplug()
            return f"Success: VIF '{vif.get_uuid()}' unplugged successfully"

    except Exception as e:
        logger.error(f"Error unplugging VIF: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def list_pifs(cluster_id: str, host_identifier: str | None = None) -> str:
    """
    List all Physical Interfaces (PIFs), optionally filtered by host.

    Args:
        cluster_id: The identifier of the cluster.
        host_identifier: Optional name or UUID of a host to filter PIFs.

    Returns:
        A formatted string containing a list of PIFs with their device, MAC, MTU, and IP addresses.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            # Get all PIFs
            pifs = PIF.get_all(session)

            # If host_identifier is provided, resolve host for filtering
            filter_host = None
            if host_identifier:
                filter_host = resolve_host(session, host_identifier)
                if not filter_host:
                    return format_error(
                        f"Host '{host_identifier}' not found", code="resource_not_found"
                    )

            pif_list = []
            for pif in pifs:
                try:
                    # Filter by host if specified
                    if filter_host:
                        pif_record = pif.get_record()
                        pif_host_ref = pif_record.get("host")
                        # Get host UUID from the PIF's host reference
                        pif_host_uuid = session.xenapi.host.get_uuid(pif_host_ref)
                        if pif_host_uuid != filter_host.get_uuid():
                            continue

                    pif_info = {
                        "uuid": pif.get_uuid(),
                        "device": pif.get_device(),
                        "mac": pif.get_mac(),
                        "mtu": pif.get_mtu(),
                        "attached": pif.get_attached(),
                    }

                    # Add IP information if available
                    try:
                        ipv4 = pif.get_address_v4()
                        if ipv4:
                            pif_info["ipv4_address"] = ipv4
                    except Exception:
                        pass

                    try:
                        ipv6 = pif.get_address_v6()
                        if ipv6:
                            pif_info["ipv6_address"] = ipv6
                    except Exception:
                        pass

                    try:
                        gateway = pif.get_gateway_v4()
                        if gateway:
                            pif_info["ipv4_gateway"] = gateway
                    except Exception:
                        pass

                    pif_list.append(pif_info)
                except Exception:
                    continue

            location_msg = f" on host '{filter_host.get_name()}'" if filter_host else ""
            return format_success(
                pif_list, f"Found {len(pif_list)} PIF(s){location_msg}"
            )
    except Exception as e:
        logger.error(f"Error listing PIFs: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_pif_info(cluster_id: str, pif_identifier: str) -> str:
    """
    Get detailed information about a specific Physical Interface (PIF).

    Args:
        cluster_id: The identifier of the cluster.
        pif_identifier: The UUID of the PIF.

    Returns:
        A formatted string containing detailed PIF record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            pif = PIF.get_by_uuid(session, pif_identifier)
            if not pif:
                return format_error(
                    f"PIF '{pif_identifier}' not found", code="resource_not_found"
                )

            pif_data = {
                "uuid": pif.get_uuid(),
                "device": pif.get_device(),
                "mac": pif.get_mac(),
                "mtu": pif.get_mtu(),
                "attached": pif.get_attached(),
            }

            # Add IP information if available
            try:
                ipv4 = pif.get_address_v4()
                if ipv4:
                    pif_data["ipv4_address"] = ipv4
            except Exception:
                pass

            try:
                ipv6 = pif.get_address_v6()
                if ipv6:
                    pif_data["ipv6_address"] = ipv6
            except Exception:
                pass

            try:
                gateway = pif.get_gateway_v4()
                if gateway:
                    pif_data["ipv4_gateway"] = gateway
            except Exception:
                pass

            return format_success(pif_data, f"PIF Info for {pif_identifier}")

    except Exception as e:
        logger.error(f"Error getting PIF info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def get_pool_info(cluster_id: str) -> str:
    """
    Get pool information and statistics.

    Args:
        cluster_id: The identifier of the cluster.

    Returns:
        A formatted string containing detailed pool record information.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

        with xapi_session(cluster_id, config) as session:
            # Get pool reference (single pool per cluster)
            pool_refs = session.xenapi.pool.get_all()
            if not pool_refs:
                return format_error(
                    "No pool found in cluster", code="resource_not_found"
                )

            pool_ref = pool_refs[0]
            pool_record = session.xenapi.pool.get_record(pool_ref)

            return format_success(pool_record, f"Pool Info for {cluster_id}")

    except Exception as e:
        logger.error(f"Error getting pool info: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.tool()
def list_pool_members(cluster_id: str) -> str:
    """
    List all hosts in the pool (members).

    Args:
        cluster_id: The identifier of the cluster.

    Returns:
        A formatted string containing a list of pool members with their name, UUID, and address.
    """
    try:
        config = load_cluster_config()
        error = validate_cluster_id(config, cluster_id)
        if error:
            return error

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
                host_list, f"Found {len(host_list)} pool member(s) in {cluster_id}"
            )
    except Exception as e:
        logger.error(f"Error listing pool members: {str(e)}")
        return format_error(str(e), code="operation_failed")


@mcp.prompt()
def xenserver_best_practices() -> str:
    """Best practices for XenServer management using MCP"""
    return xenserver_mcp_best_practices()


@mcp.prompt()
def vm_lifecycle() -> str:
    """VM Lifecycle Management Workflow guide"""
    return vm_lifecycle_workflow()


@mcp.prompt()
def storage_management() -> str:
    """Storage Management Workflow guide"""
    return storage_management_workflow()


@mcp.prompt()
def network_management() -> str:
    """Network Management Workflow guide"""
    return network_management_workflow()


@mcp.prompt()
def host_maintenance() -> str:
    """Host Maintenance Workflow guide"""
    return host_maintenance_workflow()


def main():
    """Main entry point for the XenServer MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
