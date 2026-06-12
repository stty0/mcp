output "vpc_id" {
  value = samsungcloudplatformv2_vpc_vpc.tier3.id
}

output "lb_public_ip" {
  value = samsungcloudplatformv2_vpc_publicip.lb.publicip.ip_address
}

output "web_servers" {
  description = "Web tier server details (incl. IDs and network info)"
  value       = samsungcloudplatformv2_virtualserver_server.web
}

output "was_servers" {
  description = "WAS tier server details (incl. IDs and network info)"
  value       = samsungcloudplatformv2_virtualserver_server.was
}

output "db_cluster_id" {
  value = samsungcloudplatformv2_mysql_cluster.db.id
}
