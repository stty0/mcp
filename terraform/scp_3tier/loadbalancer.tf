# Load balancer for the web tier, placed in the web subnet
resource "samsungcloudplatformv2_loadbalancer_loadbalancer" "web" {
  loadbalancer_create = {
    name                     = "tier3-web-lb"
    description              = "Load balancer for the web tier"
    layer_type               = "L7"
    firewall_enabled         = true
    firewall_logging_enabled = false
    vpc_id                   = samsungcloudplatformv2_vpc_vpc.tier3.id
    subnet_id                = samsungcloudplatformv2_vpc_subnet.web.id
    service_ip               = null
    source_nat_ip            = null
    health_check_ip_1        = null
    health_check_ip_2        = null
  }
}

# Map the load balancer's service IP to the public IP for internet access
resource "samsungcloudplatformv2_loadbalancer_loadbalancer_public_nat_ip" "web" {
  loadbalancer_id = samsungcloudplatformv2_loadbalancer_loadbalancer.web.id

  static_nat_create = {
    publicip_id = samsungcloudplatformv2_vpc_publicip.lb.id
  }

  depends_on = [samsungcloudplatformv2_firewall_firewall_rule.lb_inbound]
}

# Health check used by the web tier server group
resource "samsungcloudplatformv2_loadbalancer_lb_health_check" "web" {
  lb_health_check_create = {
    name                  = "tier3-web-health-check"
    description           = "Health check for the web tier"
    vpc_id                = samsungcloudplatformv2_vpc_vpc.tier3.id
    subnet_id             = samsungcloudplatformv2_vpc_subnet.web.id
    protocol              = "HTTP"
    health_check_port     = var.web_listen_port
    health_check_interval = 30
    health_check_timeout  = 5
    health_check_count    = 3
    http_method           = "GET"
    health_check_url      = "/"
    response_code         = "200"
  }
}

# Server group containing the web tier instances
resource "samsungcloudplatformv2_loadbalancer_lb_server_group" "web" {
  lb_server_group_create = {
    name               = "tier3-web-server-group"
    description        = "Server group for the web tier"
    vpc_id             = samsungcloudplatformv2_vpc_vpc.tier3.id
    subnet_id          = samsungcloudplatformv2_vpc_subnet.web.id
    protocol           = "HTTP"
    lb_method          = "ROUND_ROBIN"
    lb_health_check_id = samsungcloudplatformv2_loadbalancer_lb_health_check.web.id
  }
}

# HTTP listener forwarding to the web tier server group
resource "samsungcloudplatformv2_loadbalancer_lb_listener" "web_http" {
  lb_listener_create = {
    name                  = "tier3-web-http"
    description           = "HTTP listener for the web tier"
    loadbalancer_id       = samsungcloudplatformv2_loadbalancer_loadbalancer.web.id
    protocol              = "HTTP"
    service_port          = 80
    routing_action        = "LB_SERVER_GROUP"
    server_group_id       = samsungcloudplatformv2_loadbalancer_lb_server_group.web.id
    persistence           = "source-ip"
    response_timeout      = 60
    session_duration_time = 120
  }
}

# Register each web tier instance as a member of the server group
resource "samsungcloudplatformv2_loadbalancer_lb_member" "web" {
  for_each = { for idx, server in samsungcloudplatformv2_virtualserver_server.web : idx => server }

  lb_server_group_id = samsungcloudplatformv2_loadbalancer_lb_server_group.web.id

  lb_member_create = {
    name = "tier3-web-member-${each.key}"
    # Private IP that SCP assigns to the instance's "web" network attachment
    member_ip   = each.value.networks["web"].fixed_ip
    member_port = var.web_listen_port
    object_type = "VM"
    object_id   = each.value.id
  }
}
