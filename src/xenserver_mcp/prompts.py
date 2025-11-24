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
