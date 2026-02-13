# XenServer MCP Troubleshooting Guide & Example Workflows

This guide provides solutions for common issues and examples of how to use the XenServer MCP tools for typical administrative tasks.

## Troubleshooting Common Issues

### 1. Connection Failures
**Symptoms:**
- Error: "Not connected to any cluster"
- Error: "Failed to connect to cluster: [Errno 61] Connection refused"

**Solutions:**
- Verify `config/clusters.json` exists and contains correct host, username, and password.
- Ensure the XenServer/XCP-ng host is reachable over the network.
- Check if the XenAPI (HTTPS/443) is enabled on the host.
- Verify that the user has sufficient permissions (Pool Admin or VM Admin).

### 2. Resource Not Found
**Symptoms:**
- Error: "VM 'my-vm' not found"
- Error: "SR 'local-storage' not found"

**Solutions:**
- Use `list_vms`, `list_storage_repositories`, or `list_hosts` to verify the exact name or UUID.
- Remember that identifiers are case-sensitive if using names.
- If a resource was recently created, try again after a few seconds or use `scan_sr` for storage-related issues.

### 3. Operation Failed (Async Tasks)
**Symptoms:**
- Error: "Operation failed: VM_BAD_POWER_STATE"
- Error: "Operation failed: HANDLE_INVALID"

**Solutions:**
- Check the current state of the resource using `get_vm_info` or `get_host_info`.
- For `VM_BAD_POWER_STATE`, ensure the VM is in the correct state for the operation (e.g., 'Halted' to start, 'Running' to shutdown).
- If a task hangs, check the XenServer logs or use the XenCenter console to see if there are underlying hardware issues.

### 4. Guest Metrics Unavailable
**Symptoms:**
- Error: "Guest metrics not available for VM"

**Solutions:**
- Ensure XenServer PV Tools (Guest Tools) are installed and running inside the VM.
- Verify the VM is in the 'Running' state.
- It may take a minute after VM startup for metrics to become available.

---

## Example Workflows

### Workflow 1: Deploying a New VM from Template

1. **Find a template:**
   `list_vm_templates(cluster_id="prod")`
2. **Provision the VM:**
   `provision_vm(cluster_id="prod", vm_identifier="Ubuntu Noble 24.04")`
3. **Configure resources:**
   `set_vm_vcpus(cluster_id="prod", vm_identifier="new-vm-uuid", vcpus=2)`
   `set_vm_memory(cluster_id="prod", vm_identifier="new-vm-uuid", memory_bytes=4294967296)`
4. **Start the VM:**
   `start_vm(cluster_id="prod", vm_identifier="new-vm-uuid")`

### Workflow 2: Host Maintenance live-migration

1. **Disable the host:**
   `disable_host(cluster_id="prod", host_identifier="xenserver-01")`
2. **Evacuate the host:**
   `evacuate_host(cluster_id="prod", host_identifier="xenserver-01")`
3. **Perform maintenance (outside MCP)**
4. **Re-enable the host:**
   `enable_host(cluster_id="prod", host_identifier="xenserver-01")`

### Workflow 3: Expanding VM Storage

1. **Find the disk:**
   `list_vm_disks(cluster_id="prod", vm_identifier="web-server")`
2. **Resize the VDI:**
   `resize_vdi(cluster_id="prod", vdi_identifier="vdi-uuid", new_size_bytes=107374182400)` (100GB)
3. **Scan the SR:**
   `scan_sr(cluster_id="prod", sr_identifier="sr-uuid")`
4. **Inside the Guest OS:**
   Resize the partition and filesystem to recognize the new space.
