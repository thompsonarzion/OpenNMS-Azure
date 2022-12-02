output "HorizonVM_public_Address" {
  value = azurerm_public_ip.HorizonVMPubipaddr.ip_address
}

output "VM_Nodes_ipAddress" {
  value = join(",", azurerm_network_interface.NodeVMinternalIP.*.private_ip_address)
}

output "tls_private_key" {
  value     = tls_private_key.connection_key.private_key_pem
  sensitive = true
}
