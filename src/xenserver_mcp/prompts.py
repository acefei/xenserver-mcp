"""MCP prompts for XenServer workflow guidance"""


def xenserver_mcp_best_practices() -> str:
    return """Provides best practices for XenServer management using MCP

1. Connection Management:
   - Always use 'list_clusters' to see available clusters
   - Use 'connect_cluster' to establish connection before operations
   - Check 'get_current_cluster' to verify which cluster you're working with

2. VM Operations:
   - Use 'list_vms' to discover available VMs
   - Always use 'get_vm_info' to check VM state before power operations
   - Prefer 'clean_shutdown' and 'clean_reboot' over forced operations
   - Create snapshots before making major changes

3. Resource Planning:
   - Check 'list_hosts' to see available resources
   - Use 'list_storage_repositories' to verify storage capacity
   - Monitor host memory and CPU usage before VM placement

4. Safety Guidelines:
   - Always verify VM/host identifiers before operations
   - Use snapshots before major changes
   - Prefer clean shutdowns over force operations
   - Check pool HA status for critical workloads

5. Troubleshooting:
   - Check guest metrics for OS-level information
   - Verify network configuration with 'list_networks'
   - Review storage utilization with 'list_storage_repositories'
   - Use 'get_host_info' to diagnose host-level issues

6. Workflow Order:
   For VM deployment:
   1. Connect to cluster
   2. Check available templates
   3. Verify storage and network resources
   4. Create/clone VM
   5. Configure networking and storage
   6. Start VM and verify guest metrics
"""


def vm_lifecycle_workflow() -> str:
    return """VM Lifecycle Management Workflow:

1. Pre-Deployment:
   - Use 'list_templates' to find suitable base template
   - Check 'list_storage_repositories' for available storage
   - Verify 'list_networks' for network configuration
   - Check 'list_hosts' for resource availability

2. Deployment:
   - Clone from template or create new VM
   - Configure vCPUs and memory allocation
   - Attach to appropriate network(s)
   - Allocate storage from appropriate SR

3. Running Operations:
   - Use 'vm_power_control' with action='start'
   - Monitor with 'get_vm_info' for guest metrics
   - Create snapshots before changes with 'create_vm_snapshot'

4. Maintenance:
   - Use 'clean_shutdown' before host maintenance
   - Create regular snapshots for backup
   - Monitor storage usage with 'list_virtual_disks'

5. Troubleshooting:
   - Check power state with 'get_vm_info'
   - Verify guest metrics (IP addresses, OS info)
   - Review VBD and VIF configurations
   - Check host resources if VM won't start

6. Decommissioning:
   - Shutdown VM cleanly
   - Export important data
   - Delete snapshots if no longer needed
   - Remove VM and associated VDIs
"""


def storage_management_workflow() -> str:
    return """Storage Management Workflow:

1. Discovery:
   - Use 'list_storage_repositories' to see all SRs and their utilization
   - Use 'get_sr_info' to see VDIs within a specific SR
   - Use 'list_vdis' to find specific virtual disks across the cluster

2. Maintenance:
   - Use 'scan_sr' to refresh SR content after manual changes or LUN resizing
   - Use 'get_vdi_info' to check VDI physical utilization vs virtual size
   - Use 'resize_vdi' to expand disk capacity (requires filesystem resize in guest)

3. VM Disk Operations:
   - Use 'list_vm_disks' to see all VBDs (Virtual Block Devices) for a VM
   - Use 'attach_disk_to_vm' to add an existing VDI to a VM
   - Use 'detach_disk_from_vm' to safely remove a disk from a VM
   - Use 'mount_iso' and 'eject_iso' for CD/DVD operations
"""


def network_management_workflow() -> str:
    return """Network Management Workflow:

1. Infrastructure:
   - Use 'list_networks' to see available virtual networks
   - Use 'list_pifs' to see physical interfaces and their IP configurations
   - Use 'get_network_info' to check MTU and bridge information

2. VM Connectivity:
   - Use 'list_vm_vifs' to see all virtual interfaces for a VM
   - Use 'get_vif_info' to check MAC addresses and network attachments
   - Use 'plug_vif' and 'unplug_vif' for hot-plugging network interfaces
"""


def host_maintenance_workflow() -> str:
    return """Host Maintenance Workflow:

1. Preparation:
   - Use 'get_host_metrics' to check current load and memory availability
   - Use 'disable_host' to prevent new VMs from starting on the host

2. Evacuation:
   - Use 'evacuate_host' to live-migrate all running VMs to other pool members
   - Verify all VMs have moved using 'list_vms' or 'get_host_info'

3. Post-Maintenance:
   - Use 'enable_host' to allow VM placement again
   - Optionally use 'reboot_vm' or 'start_vm' for any VMs that were shut down
"""
