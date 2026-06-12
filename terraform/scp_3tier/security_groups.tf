# Web tier security group: accepts traffic from the load balancer
resource "samsungcloudplatformv2_security_group_security_group" "web" {
  name        = "tier3-web-sg"
  description = "Security group for web tier servers"
}

resource "samsungcloudplatformv2_security_group_security_group_rule" "web_ingress_http" {
  security_group_id = samsungcloudplatformv2_security_group_security_group.web.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "TCP"
  port_range_min    = var.web_listen_port
  port_range_max    = var.web_listen_port
  remote_ip_prefix  = var.vpc_cidr
  description       = "Allow HTTP from the load balancer"
}

# WAS tier security group: accepts traffic only from the web tier
resource "samsungcloudplatformv2_security_group_security_group" "was" {
  name        = "tier3-was-sg"
  description = "Security group for WAS tier servers"
}

resource "samsungcloudplatformv2_security_group_security_group_rule" "was_ingress_from_web" {
  security_group_id = samsungcloudplatformv2_security_group_security_group.was.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "TCP"
  port_range_min    = var.was_listen_port
  port_range_max    = var.was_listen_port
  remote_group_id   = samsungcloudplatformv2_security_group_security_group.web.id
  description       = "Allow application traffic from the web tier"
}
