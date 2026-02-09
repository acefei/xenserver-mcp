import json
from typing import Any, Dict, List, Optional, Union

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
