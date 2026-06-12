# VPC for the 3-tier architecture
resource "samsungcloudplatformv2_vpc_vpc" "tier3" {
  name        = "tier3-vpc"
  cidr        = var.vpc_cidr
  description = "VPC for SCP 3-Tier Architecture"
}

# Web tier subnet: load balancer + web servers
resource "samsungcloudplatformv2_vpc_subnet" "web" {
  name        = "tier3-web-subnet"
  vpc_id      = samsungcloudplatformv2_vpc_vpc.tier3.id
  type        = "GENERAL"
  cidr        = var.web_subnet_cidr
  description = "Web tier subnet"
}

# WAS tier subnet: application servers
resource "samsungcloudplatformv2_vpc_subnet" "was" {
  name        = "tier3-was-subnet"
  vpc_id      = samsungcloudplatformv2_vpc_vpc.tier3.id
  type        = "GENERAL"
  cidr        = var.was_subnet_cidr
  description = "WAS tier subnet"
}

# DB tier subnet: MySQL cluster
resource "samsungcloudplatformv2_vpc_subnet" "db" {
  name        = "tier3-db-subnet"
  vpc_id      = samsungcloudplatformv2_vpc_vpc.tier3.id
  type        = "GENERAL"
  cidr        = var.db_subnet_cidr
  description = "DB tier subnet"
}

# Internet gateway with its managed firewall, used for the LB's public endpoint
resource "samsungcloudplatformv2_vpc_internet_gateway" "tier3" {
  vpc_id           = samsungcloudplatformv2_vpc_vpc.tier3.id
  type             = "IGW"
  description      = "Internet gateway for the 3-tier architecture"
  firewall_enabled = true
}

# Public IP for the load balancer's internet-facing endpoint
resource "samsungcloudplatformv2_vpc_publicip" "lb" {
  type        = "IGW"
  description = "Public IP for the web load balancer"

  depends_on = [samsungcloudplatformv2_vpc_internet_gateway.tier3]
}

# Allow inbound HTTP/HTTPS from users to the load balancer's public IP
resource "samsungcloudplatformv2_firewall_firewall_rule" "lb_inbound" {
  firewall_id = samsungcloudplatformv2_vpc_internet_gateway.tier3.internet_gateway.firewall_id

  firewall_rule_create = {
    action              = "ALLOW"
    direction           = "INBOUND"
    description         = "Allow HTTP/HTTPS to the web load balancer"
    source_address      = [var.allowed_web_cidr]
    destination_address = [samsungcloudplatformv2_vpc_publicip.lb.publicip.ip_address]
    status              = "ENABLE"
    service = [
      {
        service_type  = "TCP"
        service_value = "80"
      },
      {
        service_type  = "TCP"
        service_value = "443"
      },
    ]
  }
}
