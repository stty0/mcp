# Login node + Slurm controller (slurmctld) + cluster monitoring node
resource "samsungcloudplatformv2_baremetal_baremetal" "management" {
  image_id         = var.image_id
  os_user_id       = var.os_user_id
  os_user_password = var.os_user_password
  region_id        = var.region_id
  vpc_id           = samsungcloudplatformv2_vpc_vpc.hpc.id
  subnet_id        = samsungcloudplatformv2_vpc_subnet.mgmt.id

  server_details = [
    {
      bare_metal_server_name = "login-node"
      nat_enabled            = true
      public_ip_address_id   = samsungcloudplatformv2_vpc_publicip.login_node.id
      server_type_id         = var.login_server_type_id
      use_hyper_threading    = true
      state                  = "RUNNING"
    },
    {
      bare_metal_server_name = "slurm-ctrl"
      nat_enabled            = false
      server_type_id         = var.controller_server_type_id
      use_hyper_threading    = true
      state                  = "RUNNING"
    },
    {
      bare_metal_server_name = "monitoring"
      nat_enabled            = false
      server_type_id         = var.controller_server_type_id
      use_hyper_threading    = true
      state                  = "RUNNING"
    },
  ]

  tags = {
    cluster = "hpc-slurm"
    role    = "management"
  }
}

# Slurm compute nodes (slurmd), wired to the local RDMA/MPI subnet
resource "samsungcloudplatformv2_baremetal_baremetal" "compute_nodes" {
  image_id         = var.image_id
  os_user_id       = var.os_user_id
  os_user_password = var.os_user_password
  region_id        = var.region_id
  vpc_id           = samsungcloudplatformv2_vpc_vpc.hpc.id
  subnet_id        = samsungcloudplatformv2_vpc_subnet.mgmt.id

  use_placement_group  = true
  placement_group_name = "hpc-compute-pg"

  server_details = [
    for i in range(var.compute_node_count) : {
      bare_metal_server_name     = format("compute-node%d", i + 1)
      nat_enabled                = false
      server_type_id             = var.compute_server_type_id
      bare_metal_local_subnet_id = samsungcloudplatformv2_vpc_subnet.rdma.id
      use_hyper_threading        = true
      state                      = "RUNNING"
    }
  ]

  tags = {
    cluster = "hpc-slurm"
    role    = "compute"
  }
}
