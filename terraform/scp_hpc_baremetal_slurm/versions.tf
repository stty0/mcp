terraform {
  required_version = ">= 1.11"

  required_providers {
    samsungcloudplatformv2 = {
      source  = "SamsungSDSCloud/samsungcloudplatformv2"
      version = "~> 3.3"
    }
  }
}

# Credentials are read from the SCP_TF_ACCESS_KEY / SCP_TF_SECRET_KEY /
# SCP_TF_AUTH_URL / SCP_TF_DEFAULT_REGION environment variables, or from
# ~/.scpconf/credentials.json + ~/.scpconf/config.json.
provider "samsungcloudplatformv2" {
}
