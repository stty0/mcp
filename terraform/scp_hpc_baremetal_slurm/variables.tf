variable "region_id" {
  type        = string
  description = "SCP region ID where the HPC cluster will be provisioned"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the HPC VPC"
  default     = "192.168.0.0/16"
}

variable "mgmt_subnet_cidr" {
  type        = string
  description = "CIDR block for the management subnet (login node, Slurm controller, monitoring, shared FS)"
  default     = "192.168.0.0/24"
}

variable "rdma_subnet_cidr" {
  type        = string
  description = "CIDR block for the local RDMA/MPI interconnect subnet between compute nodes"
  default     = "192.168.1.0/24"
}

variable "image_id" {
  type        = string
  description = "OS image ID used for all bare metal servers (e.g. an HPC-ready Linux image)"
}

variable "os_user_id" {
  type        = string
  description = "OS user ID for all bare metal servers"
}

variable "os_user_password" {
  type        = string
  description = "OS user password for all bare metal servers"
  sensitive   = true
}

variable "login_server_type_id" {
  type        = string
  description = "Bare metal server type ID for the Slurm login node"
}

variable "controller_server_type_id" {
  type        = string
  description = "Bare metal server type ID for the Slurm controller and cluster monitoring nodes"
}

variable "compute_server_type_id" {
  type        = string
  description = "Bare metal server type ID for the Slurm compute nodes"
}

variable "compute_node_count" {
  type        = number
  description = "Number of Slurm compute nodes (max 5 per baremetal_baremetal resource)"
  default     = 3

  validation {
    condition     = var.compute_node_count >= 1 && var.compute_node_count <= 5
    error_message = "compute_node_count must be between 1 and 5."
  }
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR range allowed to SSH/sbatch into the login node's public IP"
  default     = "0.0.0.0/0"
}
