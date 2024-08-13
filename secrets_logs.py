import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from logging import getLogger

logger = getLogger(__name__)

load_dotenv(override=True)


class Config:
    """Base configuration class."""

    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    # Add other static or environment-based configurations here.


class SecretManager:
    """Manages secrets from Azure Key Vault or environment variables."""

    def __init__(self, use_key_vault=True):
        self.use_key_vault = use_key_vault
        self.key_vault_name = os.getenv("KEY_VAULT_NAME", "kviaofertaidealdllo001")
        self.kv_uri = f"https://{self.key_vault_name}.vault.azure.net"
        self.credential = (
            DefaultAzureCredential()
        )
        self.client = (
            SecretClient(vault_url=self.kv_uri, credential=self.credential)
            if use_key_vault
            else None
        )

    def get_secret(self, name):
        """Retrieve secret from Azure Key Vault or environment."""
        if self.use_key_vault:
            try:
                secret = self.client.get_secret(name).value
                logger.info(f"Secret {name} fetched from Key Vault.")
                return secret
            except Exception as e:
                logger.error(f"Failed to fetch {name} from Key Vault: {e}")
        # Fallback to environment variable if Key Vault fails or not used
        secret = os.getenv(name)
        if secret:
            logger.info(f"Secret {name} fetched from environment.")
        else:
            logger.error(f"Secret {name} not found in environment.")
        return secret


# Create an instance of SecretManager
# secret_manager = SecretManager()

# Usage within the application
# Config.AZURE_OPENAI_API_KEY = secret_manager.get_secret("AZURE-OPENAI-API-KEY")
# Add other secret fetches as needed.


# # Optionally: Define a function to load all necessary secrets at once.
# def load_secrets():
#     """Loads all necessary secrets into the configuration."""
#     secrets = [
#         "AZURE_OPENAI_API_KEY",
#         "AZURE_CLIENT_ID",
#         "COSMOS_CONNECTION_STRING",
#         ...,
#     ]  # List all needed secrets
#     for secret_name in secrets:
#         setattr(Config, secret_name, secret_manager.get_secret(secret_name))


# # load_secrets()
