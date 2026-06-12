# Shared parallel filesystem mounted by all Slurm compute nodes
resource "samsungcloudplatformv2_filestorage_volume" "shared_fs" {
  name      = "hpc-shared-fs"
  protocol  = "NFS"
  type_name = "HighPerformanceSSD"

  access_rules = [
    for server in samsungcloudplatformv2_baremetal_baremetal.compute_nodes.server_details : {
      object_type = "BM"
      object_id   = server.id
    }
  ]

  tags = {
    cluster = "hpc-slurm"
  }
}
