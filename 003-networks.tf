resource "azurerm_virtual_network" "HorizonVM" {
  name                = "opennms-bm-hvm-network"
  address_space       = ["172.21.0.0/16"]
  location            = azurerm_resource_group.HorizonVM.location
  resource_group_name = azurerm_resource_group.HorizonVM.name
  tags                = var.tags
}

resource "azurerm_subnet" "HorizonVM" {
  name                 = "65k"
  resource_group_name  = azurerm_resource_group.HorizonVM.name
  virtual_network_name = azurerm_virtual_network.HorizonVM.name
  address_prefixes     = ["172.21.0.0/16"]

}

resource "azurerm_network_interface" "HorizonVM" {
  name                = "opennms-bm-hvm-nic"
  location            = azurerm_resource_group.HorizonVM.location
  resource_group_name = azurerm_resource_group.HorizonVM.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.HorizonVM.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.HorizonVMPubipaddr.id
  }
  tags = var.tags

}

resource "azurerm_network_security_group" "HorizonVM" {
  name                = "opennms-bm-hvm-secgrp"
  location            = azurerm_resource_group.HorizonVM.location
  resource_group_name = azurerm_resource_group.HorizonVM.name

  security_rule = [
    { access                                     = "Deny"
      description                                = "SSH Rule"
      destination_address_prefix                 = "*"
      destination_address_prefixes               = []
      destination_port_range                     = "22"
      destination_port_ranges                    = []
      direction                                  = "Inbound"
      name                                       = "SSH"
      priority                                   = 100
      protocol                                   = "Tcp"
      source_address_prefix                      = "*"
      source_address_prefixes                    = []
      source_port_range                          = "22"
      source_port_ranges                         = []
      source_application_security_group_ids      = []
      destination_application_security_group_ids = []
    },
    { access                                     = "Allow"
      description                                = "OpenNMS Rule"
      destination_address_prefix                 = "*"
      destination_address_prefixes               = []
      destination_port_range                     = "8980"
      destination_port_ranges                    = []
      direction                                  = "Inbound"
      name                                       = "OpenNMS"
      priority                                   = 101
      protocol                                   = "Tcp"
      source_address_prefix                      = "*"
      source_address_prefixes                    = []
      source_port_range                          = "8980"
      source_port_ranges                         = []
      source_application_security_group_ids      = []
      destination_application_security_group_ids = []
  }]

  tags = var.tags
}


resource "azurerm_public_ip" "HorizonVMPubipaddr" {
  name                = "opennms-bm-hvm-pubaddr"
  location            = azurerm_resource_group.HorizonVM.location
  resource_group_name = azurerm_resource_group.HorizonVM.name
  allocation_method   = "Static"
  tags                = var.tags
}
