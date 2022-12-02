variable "resource_group_location" {
  default     = "eastus"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  default     = "Benchmark"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "vm_size" {
  default     = "Standard_D2s_v3"
  description = "The resource size for the Horizon Virtual machine"
}

variable "tags" {
  type        = map(string)
  description = "A map of the tags to use on the resources that are deployed with this module."

  default = {
    Owner   = "",
    Team    = "Horizon",
    Project = "Benchmark"
  }
}

variable "child_node_numbers" {
  description = "Number of child nodes we want to have"
  type        = number
  default     = 0
}
