terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  lower   = true
  numeric = true
  special = false
}

resource "azurerm_storage_account" "storage" {
  name                     = "storagedemoflenne${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "demo"
  }
}

resource "azurerm_storage_container" "container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}



################   for the function part ##############################################

resource "azurerm_log_analytics_workspace" "law" {
  name                = "${azurerm_resource_group.rg.name}-law"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "ai" {
  name                = "${azurerm_resource_group.rg.name}-ai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.law.id
}



resource "azurerm_app_service_plan" "plan" {
  name                = "${azurerm_resource_group.rg.name}-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  kind     = "FunctionApp"
  reserved = true

  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

resource "azurerm_linux_function_app" "func" {
  name                       = var.function_app_name
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  service_plan_id            = azurerm_app_service_plan.plan.id

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  # <-- ICI (au niveau racine, pas dans site_config)
  functions_extension_version = "~4"

  site_config {
    application_stack {
      python_version = var.python_version # "3.10" ou "3.11"
    }
    # nothing else needed
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME              = "python"
    AzureWebJobsStorage                   = azurerm_storage_account.storage.primary_connection_string
    SCM_DO_BUILD_DURING_DEPLOYMENT        = "1"  # build Oryx à partir de requirements.txt
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.ai.connection_string

    # environment variables
    AZURE_CONTAINER_NAME = var.container_name
    AZURE_STORAGE_CONNECTION_STRING = azurerm_storage_account.storage.primary_connection_string
  }

  identity { type = "SystemAssigned" }

  tags = { environment = "demo" }
}



################ output ##################################


output "container_url" {
  value = "${azurerm_storage_account.storage.primary_blob_endpoint}${azurerm_storage_container.container.name}"
}

output "function_app_name"       { value = azurerm_linux_function_app.func.name }
output "function_default_host"   { value = azurerm_linux_function_app.func.default_hostname }
