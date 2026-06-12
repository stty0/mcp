output "vpc_id" {
  value = samsungcloudplatformv2_vpc_vpc.hpc.id
}

output "login_node_public_ip" {
  value = samsungcloudplatformv2_vpc_publicip.login_node.publicip.ip_address
}

output "management_servers" {
  description = "login-node, slurm-ctrl, monitoring server details (incl. IDs)"
  value       = samsungcloudplatformv2_baremetal_baremetal.management.server_details
}

output "compute_node_servers" {
  description = "Slurm compute node server details (incl. IDs)"
  value       = samsungcloudplatformv2_baremetal_baremetal.compute_nodes.server_details
}

output "shared_fs_endpoint" {
  value = samsungcloudplatformv2_filestorage_volume.shared_fs.endpoint_path
}
