# Available XenServer MCP Tools

## Read-Only / Information Tools
1. `xenserver_list_clusters` - List all configured clusters
2. `xenserver_list_vms` - List VMs in a cluster
3. `xenserver_get_vm_info` - Get detailed VM info
4. `xenserver_list_vm_templates` - List VM templates
5. `xenserver_list_vm_snapshots` - List VM snapshots
6. `xenserver_get_vm_guest_metrics` - Get guest OS metrics
7. `xenserver_get_vm_console_url` - Get console URL (not implemented)
8. `xenserver_list_vm_disks` - List attached disks
9. `xenserver_list_hosts` - List hosts in cluster
10. `xenserver_get_host_info` - Get detailed host info
11. `xenserver_get_host_metrics` - Get host CPU/RAM metrics
12. `xenserver_get_host_capabilities` - Get host capabilities
13. `xenserver_list_storage_repositories` - List SRs
14. `xenserver_get_sr_info` - Get detailed SR info
15. `xenserver_scan_sr` - Scan SR for changes (Safe action)
16. `xenserver_list_vdis` - List VDIs
17. `xenserver_get_vdi_info` - Get detailed VDI info
18. `xenserver_list_networks` - List networks
19. `xenserver_get_network_info` - Get detailed network info
20. `xenserver_list_vm_vifs` - List VM network interfaces
21. `xenserver_get_vif_info` - Get detailed VIF info
22. `xenserver_list_pifs` - List physical interfaces
23. `xenserver_get_pif_info` - Get detailed PIF info
24. `xenserver_get_pool_info` - Get pool info
25. `xenserver_list_pool_members` - List pool members

## Write / Action Tools
26. `xenserver_start_vm`
27. `xenserver_shutdown_vm`
28. `xenserver_reboot_vm`
29. `xenserver_suspend_vm`
30. `xenserver_resume_vm`
31. `xenserver_pause_vm`
32. `xenserver_unpause_vm`
33. `xenserver_batch_start_vms`
34. `xenserver_batch_shutdown_vms`
35. `xenserver_create_vm_snapshot`
36. `xenserver_delete_vm_snapshot`
37. `xenserver_clone_vm`
38. `xenserver_copy_vm`
39. `xenserver_delete_vm`
40. `xenserver_provision_vm`
41. `xenserver_set_vm_vcpus`
42. `xenserver_set_vm_memory`
43. `xenserver_attach_disk_to_vm`
44. `xenserver_detach_disk_from_vm`
45. `xenserver_mount_iso`
46. `xenserver_eject_iso`
47. `xenserver_enable_host`
48. `xenserver_disable_host`
49. `xenserver_evacuate_host`
50. `xenserver_resize_vdi`
51. `xenserver_clone_vdi`
52. `xenserver_delete_vdi`
53. `xenserver_plug_vif`
54. `xenserver_unplug_vif`
