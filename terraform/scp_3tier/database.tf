# DB tier: managed MySQL cluster, reachable only from the WAS tier subnet
resource "samsungcloudplatformv2_mysql_cluster" "db" {
  name                    = "appdbcluster"
  instance_name_prefix    = "appdb"
  dbaas_engine_version_id = var.db_engine_version_id
  subnet_id               = samsungcloudplatformv2_vpc_subnet.db.id
  ha_enabled              = false
  nat_enabled             = false
  timezone                = "Asia/Seoul"
  service_state           = "RUNNING"

  allowable_ip_addresses = [var.was_subnet_cidr]

  init_config_option = {
    database_name           = var.db_name
    database_user_name      = var.db_user_name
    database_user_password  = var.db_user_password
    database_port           = 3306
    database_character_set  = "utf8"
    database_case_sensitive = true

    backup_option = {
      retention_period_day     = "7"
      starting_time_hour       = "11"
      archive_frequency_minute = "30"
    }
  }

  maintenance_option = {
    use_maintenance_option = false
    period_hour            = null
    starting_day_of_week   = null
    starting_time          = null
  }

  instance_groups = [
    {
      role_type        = "ACTIVE"
      server_type_name = var.db_server_type_name

      block_storage_groups = [
        {
          role_type   = "OS"
          volume_type = "SSD"
          size_gb     = 104
        },
        {
          role_type   = "DATA"
          volume_type = "SSD"
          size_gb     = 100
        },
      ]

      instances = [
        {
          role_type = "ACTIVE"
        }
      ]
    }
  ]

  tags = {
    tier = "db"
  }
}
