resource "azurerm_linux_virtual_machine" "HorizonVM" {
  name                = "opennms-bm-horizonvm"
  resource_group_name = azurerm_resource_group.HorizonVM.name
  location            = azurerm_resource_group.HorizonVM.location
  size                = var.vm_size
  admin_username      = "opennms"
  network_interface_ids = [
    azurerm_network_interface.HorizonVM.id,
  ]

  #admin_ssh_key {
  #  username   = "opennms"
  #  public_key = file("~/.ssh/id_rsa.pub")
  #}
  admin_ssh_key {
    username   = "opennms"
    public_key = tls_private_key.connection_key.public_key_openssh
  }



  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18_04-lts-gen2"
    version   = "latest"
  }

  tags = var.tags
}

resource "azurerm_virtual_machine_extension" "HorizonVM" {
  name                 = "install_OpenNMS_Horizon"
  virtual_machine_id   = azurerm_linux_virtual_machine.HorizonVM.id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"

  settings = <<SETTINGS
    {
        "commandToExecute": "wget -O /tmp/autoinstall.sh https://raw.githubusercontent.com/mershad-manesh/test/main/autoinstall.sh  && chmod +x /tmp/autoinstall.sh && /tmp/autoinstall.sh > /home/opennms/log.txt 2>&1"
    }
SETTINGS


  tags = var.tags
}

