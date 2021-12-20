from __future__ import annotations

from azure.identity.aio import AzureCliCredential
from azure.keyvault.secrets import SecretProperties
from azure.keyvault.secrets.aio import SecretClient


class KeyVault:
    def __init__(self, vault_name: str):
        credential = AzureCliCredential()
        self.client = SecretClient(
            vault_url=f"https://{vault_name}.vault.azure.net", credential=credential
        )

    async def get_secret_value(self, name: str, version: str) -> str:

        secret = await self.client.get_secret(name=name, version=version)
        return secret.value

    async def get_secrets(self) -> list[SecretProperties]:
        properties = []
        async for p in self.client.list_properties_of_secrets():
            properties.append(p)
        return properties

    async def get_secret_versions(self, name: str) -> list[SecretProperties]:

        versions = []
        async for v in self.client.list_properties_of_secret_versions(name=name):
            versions.append(v)

        return sorted(list(versions), key=lambda d: d.created_on, reverse=True)
