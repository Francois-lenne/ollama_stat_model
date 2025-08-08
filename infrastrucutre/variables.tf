variable "container_name" {
  description = "Nom du container Blob"
  type        = string
}

variable "resource_group_name" {
  description = "Nom du groupe de ressources"
  type        = string
}

variable "location" {
  description = "Région Azure"
  type        = string
}

variable "python_version" {
  description = "Version de Python"
  type        = string
}

variable "function_app_name" {
  description = "Nom de l'application de fonction Azure"
  type        = string
  
}