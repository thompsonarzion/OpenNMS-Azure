resource "azurerm_resource_group" "HorizonVM" {
  name     = var.resource_group_name_prefix
  location = var.resource_group_location
  tags     = var.tags
}

  # Create (and display) an SSH key
  resource "tls_private_key" "connection_key" {
    algorithm = "RSA"
    rsa_bits  = 4096
  }
