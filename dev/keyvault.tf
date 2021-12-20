data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "resource-group" {
  name     = "keyvault-browser-dev-rg"
  location = "uksouth"
}

resource "azurerm_key_vault" "keyvault-browser-dev" {
  depends_on                  = [azurerm_resource_group.resource-group]
  name                        = "keyvault-browser-dev"
  location                    = "uksouth"
  resource_group_name         = "keyvault-browser-dev-rg"
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    key_permissions = [
      "get",
    ]
    secret_permissions = [
      "get", "backup", "delete", "list", "purge", "recover", "restore", "set",
    ]
  }
}

resource "random_password" "random" {
  length = 20
  special = true
}

resource "azurerm_key_vault_secret" "secret1" {
  count = 20
  name         = "TEST-PASSWORD-${count.index}"
  value        = random_password.random.result
  key_vault_id = azurerm_key_vault.keyvault-browser-dev.id
  depends_on = [ azurerm_key_vault.keyvault-browser-dev ]
}

resource "azurerm_key_vault_secret" "secret2" {
  count = 20
  name         = "PASSWORD-${count.index}-TEST"
  value        = random_password.random.result
  key_vault_id = azurerm_key_vault.keyvault-browser-dev.id
  depends_on = [ azurerm_key_vault.keyvault-browser-dev ]
}

resource "azurerm_key_vault_secret" "secret3" {
  count = 10
  name         = "PASSWORD${count.index}TEST"
  value        = random_password.random.result
  key_vault_id = azurerm_key_vault.keyvault-browser-dev.id
  depends_on = [ azurerm_key_vault.keyvault-browser-dev ]
}

resource "azurerm_key_vault_secret" "secret4" {
  count = 10
  name         = "APP-PASSWORD${count.index}"
  value        = random_password.random.result
  key_vault_id = azurerm_key_vault.keyvault-browser-dev.id
  depends_on = [ azurerm_key_vault.keyvault-browser-dev ]
}
