import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from xen_api.VM import VM
from xen_api.Host import Host
from xen_api.SR import SR
from xen_api.Network import Network
from xen_api.VDI import VDI
from xen_api.VIF import VIF
from xen_api.PIF import PIF


def resolve_vm(session, identifier: str) -> Optional[VM]:
    """
    Find a VM by UUID or name label.

    Args:
        session: Active XenAPI session
        identifier: UUID or Name Label of the VM

    Returns:
        VM object if found, None otherwise
    """
    # Try by UUID first
    try:
        vm = VM.get_by_uuid(session, identifier)
        if vm:
            return vm
    except Exception:
        pass

    # Try by Name Label
    try:
        # Note: get_by_name_label returns a list of refs
        vm_refs = session.xenapi.VM.get_by_name_label(identifier)
        if vm_refs and len(vm_refs) > 0:
            # We return the first match. In case of duplicates, this picks one arbitrarily.
            return VM(session, vm_refs[0])
    except Exception:
        pass

    return None


def resolve_host(session, identifier: str) -> Optional[Host]:
    """
    Find a Host by UUID or name label.
    """
    # Try by UUID
    try:
        host = Host.get_by_uuid(session, identifier)
        if host:
            return host
    except Exception:
        pass

    # Try by Name Label
    try:
        # Check if wrapper has get_by_name and if it handles the call correctly
        # The wrapper uses get_by_name_label but assumes single return or handles it?
        # Let's use raw API to be safe and consistent with resolve_vm
        host_refs = session.xenapi.host.get_by_name_label(identifier)
        if host_refs and len(host_refs) > 0:
            return Host(session, host_refs[0])
    except Exception:
        pass

    return None


def resolve_sr(session, identifier: str) -> Optional[SR]:
    """
    Find a Storage Repository by UUID or name label.
    """
    # Try by UUID
    try:
        sr = SR.get_by_uuid(session, identifier)
        if sr:
            return sr
    except Exception:
        pass

    # Try by Name Label
    try:
        sr_refs = session.xenapi.SR.get_by_name_label(identifier)
        if sr_refs and len(sr_refs) > 0:
            return SR(session, sr_refs[0])
    except Exception:
        pass

    return None


def resolve_network(session, identifier: str) -> Optional[Network]:
    """
    Find a Network by UUID or name label.
    """
    # Try by UUID
    try:
        network = Network.get_by_uuid(session, identifier)
        if network:
            return network
    except Exception:
        pass

    # Try by Name Label
    try:
        network_refs = session.xenapi.network.get_by_name_label(identifier)
        if network_refs and len(network_refs) > 0:
            return Network(session, network_refs[0])
    except Exception:
        pass

    return None


def resolve_vdi(session, identifier: str) -> Optional[VDI]:
    """
    Find a VDI by UUID or name label.
    """
    # Try by UUID
    try:
        vdi = VDI.get_by_uuid(session, identifier)
        if vdi:
            return vdi
    except Exception:
        pass

    # Try by Name Label
    try:
        vdi_refs = session.xenapi.VDI.get_by_name_label(identifier)
        if vdi_refs and len(vdi_refs) > 0:
            return VDI(session, vdi_refs[0])
    except Exception:
        pass

    return None


def format_success(data: Any, message: str = "") -> str:
    """
    Format a success response.
    If data is a complex object/dict, returns formatted JSON string.
    If message is provided, prepends it.
    """
    try:
        json_output = json.dumps(data, indent=2, default=str)
        if message:
            return f"{message}\n{json_output}"
        return json_output
    except Exception:
        return str(data)


def format_error(message: str, code: str | None = None, details: Any = None) -> str:
    """
    Format an error response as a JSON string, consistent with format_success output style.

    Args:
        message: Error message
        code: Optional error code
        details: Optional additional error details

    Returns:
        JSON formatted error string
    """
    error_obj = {"error": message}
    if code is not None:
        error_obj["code"] = code
    if details is not None:
        error_obj["details"] = details

    try:
        return json.dumps(error_obj, indent=2, default=str)
    except Exception:
        return json.dumps({"error": str(message)})


def validate_cluster_id(config: Dict[str, Any], cluster_id: str) -> Optional[str]:
    """
    Validate that a cluster_id exists in the configuration.

    Args:
        config: Cluster configuration dictionary
        cluster_id: Cluster ID to validate

    Returns:
        Formatted error string if invalid, None if valid
    """
    if cluster_id not in config:
        return format_error(
            f"Cluster '{cluster_id}' not found", code="cluster_not_found"
        )
    return None


def validate_required(value: Any, label: str) -> Optional[str]:
    """
    Validate that a required value is present and non-empty.

    Args:
        value: Value to validate
        label: Label for the value (used in error message)

    Returns:
        Formatted error string if invalid, None if valid
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return format_error(
            f"{label} is required and cannot be empty", code="validation_error"
        )
    return None


def validate_non_empty_list(values: Any, label: str) -> Optional[str]:
    """
    Validate that a value is a non-empty list.

    Args:
        values: Value to validate
        label: Label for the value (used in error message)

    Returns:
        Formatted error string if invalid, None if valid
    """
    if not isinstance(values, list) or len(values) == 0:
        return format_error(
            f"{label} must be a non-empty list", code="validation_error"
        )
    return None


def validate_positive_int(value: Any, label: str) -> Optional[str]:
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate
        label: Label for the value (used in error message)

    Returns:
        Formatted error string if invalid, None if valid
    """
    if not isinstance(value, int) or value <= 0:
        return format_error(
            f"{label} must be a positive integer", code="validation_error"
        )
    return None


def find_vms_by_name_pattern(session, pattern: str) -> list[VM]:
    """
    Find VMs whose name contains the specified pattern (case-insensitive substring match).

    Args:
        session: Active XenAPI session
        pattern: Substring to search for in VM names

    Returns:
        List of VM objects matching the pattern
    """
    all_vms = VM.list_vm(session)
    pattern_lower = pattern.lower()
    matching_vms = []

    for vm in all_vms:
        try:
            record = vm.get_record()
            name = record.get("name_label", "")
            if pattern_lower in name.lower():
                matching_vms.append(vm)
        except Exception:
            continue

    return matching_vms


def find_vms_by_tag(session, tag: str) -> list[VM]:
    """
    Find VMs that have the specified tag.

    Args:
        session: Active XenAPI session
        tag: Tag to search for

    Returns:
        List of VM objects with the specified tag
    """
    all_vms = VM.list_vm(session)
    matching_vms = []

    for vm in all_vms:
        try:
            record = vm.get_record()
            tags = record.get("tags", [])
            if tag in tags:
                matching_vms.append(vm)
        except Exception:
            continue

    return matching_vms


def filter_vms_by_power_state(session, vms: list[VM], power_state: str) -> list[VM]:
    """
    Filter VMs by power state.

    Args:
        session: Active XenAPI session
        vms: List of VM objects to filter
        power_state: Power state to filter by (e.g., "Running", "Halted", "Suspended", "Paused")

    Returns:
        List of VM objects in the specified power state
    """
    filtered_vms = []

    for vm in vms:
        try:
            record = vm.get_record()
            vm_power_state = record.get("power_state", "")
            if vm_power_state == power_state:
                filtered_vms.append(vm)
        except Exception:
            continue

    return filtered_vms


def retry_sync(
    fn: Callable[[], Any],
    *,
    attempts: int = 3,
    delay_seconds: float = 0.5,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Any:
    """
    Retry a synchronous function call with exponential backoff.

    Args:
        fn: Zero-argument callable to retry
        attempts: Number of attempts (default: 3)
        delay_seconds: Initial delay in seconds between retries (default: 0.5)
        retry_exceptions: Tuple of exception types to retry on (default: (Exception,))

    Returns:
        Result from successful function call

    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    for attempt in range(attempts):
        try:
            return fn()
        except retry_exceptions as e:
            last_exception = e
            if attempt < attempts - 1:
                time.sleep(delay_seconds * (2**attempt))
            continue

    if last_exception:
        raise last_exception
    raise RuntimeError("retry_sync failed with no exception")


async def retry_async(
    fn: Callable[[], Any],
    *,
    attempts: int = 3,
    delay_seconds: float = 0.5,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Any:
    """
    Retry an async function call with exponential backoff.

    Args:
        fn: Zero-argument callable returning an awaitable
        attempts: Number of attempts (default: 3)
        delay_seconds: Initial delay in seconds between retries (default: 0.5)
        retry_exceptions: Tuple of exception types to retry on (default: (Exception,))

    Returns:
        Result from successful function call

    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    for attempt in range(attempts):
        try:
            return await fn()
        except retry_exceptions as e:
            last_exception = e
            if attempt < attempts - 1:
                await asyncio.sleep(delay_seconds * (2**attempt))
            continue

    if last_exception:
        raise last_exception
    raise RuntimeError("retry_async failed with no exception")
