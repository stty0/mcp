# Web tier virtual servers, registered behind the load balancer
resource "samsungcloudplatformv2_virtualserver_server" "web" {
  count = var.web_node_count

  name           = "tier3-web-${count.index + 1}"
  keypair_name   = var.keypair_name
  image_id       = var.image_id
  server_type_id = var.web_server_type_id
  state          = "RUNNING"

  boot_volume = {
    size = 50
  }

  networks = {
    web = {
      subnet_id = samsungcloudplatformv2_vpc_subnet.web.id
    }
  }

  security_groups = [samsungcloudplatformv2_security_group_security_group.web.id]

  tags = {
    tier = "web"
  }
}

# WAS tier virtual servers, reachable only from the web tier
resource "samsungcloudplatformv2_virtualserver_server" "was" {
  count = var.was_node_count

  name           = "tier3-was-${count.index + 1}"
  keypair_name   = var.keypair_name
  image_id       = var.image_id
  server_type_id = var.was_server_type_id
  state          = "RUNNING"

  boot_volume = {
    size = 50
  }

  networks = {
    was = {
      subnet_id = samsungcloudplatformv2_vpc_subnet.was.id
    }
  }

  security_groups = [samsungcloudplatformv2_security_group_security_group.was.id]

  tags = {
    tier = "was"
  }
}
