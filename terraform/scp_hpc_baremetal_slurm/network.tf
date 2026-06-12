# VPC for the HPC cluster
resource "samsungcloudplatformv2_vpc_vpc" "hpc" {
  name        = "hpc-slurm-vpc"
  cidr        = var.vpc_cidr
  description = "VPC for SCP Bare Metal HPC Cluster (Slurm)"
}

# Management subnet: login node, Slurm controller, monitoring, shared FS access
resource "samsungcloudplatformv2_vpc_subnet" "mgmt" {
  name        = "hpc-mgmt-subnet"
  vpc_id      = samsungcloudplatformv2_vpc_vpc.hpc.id
  type        = "GENERAL"
  cidr        = var.mgmt_subnet_cidr
  description = "Management/Slurm control plane subnet"
}

# Local subnet used as the RDMA/MPI interconnect between compute nodes
resource "samsungcloudplatformv2_vpc_subnet" "rdma" {
  name        = "hpc-rdma-subnet"
  vpc_id      = samsungcloudplatformv2_vpc_vpc.hpc.id
  type        = "LOCAL"
  cidr        = var.rdma_subnet_cidr
  description = "Local RDMA/MPI interconnect subnet for compute nodes"
}

# Internet gateway with its managed firewall, used for login node SSH access
resource "samsungcloudplatformv2_vpc_internet_gateway" "hpc" {
  vpc_id           = samsungcloudplatformv2_vpc_vpc.hpc.id
  type             = "IGW"
  description      = "Internet gateway for Slurm login node access"
  firewall_enabled = true
}

# Public IP attached to the login node for ssh/sbatch access
resource "samsungcloudplatformv2_vpc_publicip" "login_node" {
  type        = "IGW"
  description = "Public IP for the Slurm login node"

  depends_on = [samsungcloudplatformv2_vpc_internet_gateway.hpc]
}

# Allow inbound SSH/sbatch to the login node's public IP
resource "samsungcloudplatformv2_firewall_firewall_rule" "login_ssh" {
  firewall_id = samsungcloudplatformv2_vpc_internet_gateway.hpc.internet_gateway.firewall_id

  firewall_rule_create = {
    action              = "ALLOW"
    direction           = "INBOUND"
    description         = "SSH/sbatch access to the Slurm login node"
    source_address      = [var.allowed_ssh_cidr]
    destination_address = [samsungcloudplatformv2_vpc_publicip.login_node.publicip.ip_address]
    status              = "ENABLE"
    service = [{
      service_type  = "TCP"
      service_value = "22"
    }]
  }
}
