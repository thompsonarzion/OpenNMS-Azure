terraform {
  required_version = ">=0.12"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.27.0"
    }
    #random = {
    #  source  = "hashicorp/random"
    #  version = "~>3.0"
    #}
    #tls = {
    #  source  = "hashicorp/tls"
    #  version = "~>4.0"
    #}
  }
  ##backend "azurerm" {
  ##  resource_group_name  = "Bechmark2"
  ##  storage_account_name = "opennmsbenchmarkdev"
  ##  container_name       = "tfstate"
  ##  key                  = "terraform.tfstate"
  ##}

}

provider "azurerm" {
  features {}
}
