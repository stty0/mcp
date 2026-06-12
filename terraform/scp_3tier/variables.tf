variable "region_id" {
  type        = string
  description = "SCP region ID where the 3-tier architecture will be provisioned"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "web_subnet_cidr" {
  type        = string
  description = "CIDR block for the web tier subnet"
  default     = "10.0.0.0/24"
}

variable "was_subnet_cidr" {
  type        = string
  description = "CIDR block for the WAS tier subnet"
  default     = "10.0.1.0/24"
}

variable "db_subnet_cidr" {
  type        = string
  description = "CIDR block for the DB tier subnet"
  default     = "10.0.2.0/24"
}

variable "image_id" {
  type        = string
  description = "OS image ID used for the web and WAS tier virtual servers"
}

variable "keypair_name" {
  type        = string
  description = "SSH keypair name used for the web and WAS tier virtual servers"
}

variable "web_server_type_id" {
  type        = string
  description = "Virtual server type ID for the web tier"
}

variable "was_server_type_id" {
  type        = string
  description = "Virtual server type ID for the WAS tier"
}

variable "web_node_count" {
  type        = number
  description = "Number of web tier virtual servers behind the load balancer"
  default     = 2
}

variable "was_node_count" {
  type        = number
  description = "Number of WAS tier virtual servers"
  default     = 2
}

variable "web_listen_port" {
  type        = number
  description = "Port on which the web tier instances serve HTTP traffic"
  default     = 80
}

variable "was_listen_port" {
  type        = number
  description = "Port on which the WAS tier instances accept requests from the web tier"
  default     = 8080
}

variable "allowed_web_cidr" {
  type        = string
  description = "CIDR range allowed to access the load balancer's public IP"
  default     = "0.0.0.0/0"
}

variable "db_engine_version_id" {
  type        = string
  description = "DBaaS engine version ID for the MySQL cluster"
}

variable "db_server_type_name" {
  type        = string
  description = "Server type name for the MySQL DB instance (e.g. db1v2m4)"
  default     = "db1v2m4"
}

variable "db_name" {
  type        = string
  description = "Initial database name"
  default     = "appdb"
}

variable "db_user_name" {
  type        = string
  description = "Initial database user name"
  default     = "appuser"
}

variable "db_user_password" {
  type        = string
  description = "Initial database user password"
  sensitive   = true
}
