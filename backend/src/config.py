"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure Cosmos DB
    cosmos_endpoint: str
    cosmos_key: str
    cosmos_database_name: str = "agent-architecture-db"

    # Azure Blob Storage
    azure_storage_connection_string: str
    azure_storage_container_name: str = "resources"

    # Azure Subscription (for resource tracking)
    azure_subscription_id: str = ""

    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_embeddings_deployment: str = "text-embedding-ada-002"
    azure_openai_api_version: str = "2024-08-01-preview"

    # Azure AI Search
    azure_search_endpoint: str
    azure_search_api_key: str
    azure_search_index_name: str = "transcripts"

    # Azure AI Foundry Model Router
    azure_ai_foundry_endpoint: str
    azure_ai_foundry_api_key: str
    model_router_deployment: str = "model-router"

    # Application
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # Authentication
    api_access_key: str

    # Microsoft Entra ID (Optional - for SSO feature, Developer B)
    entra_client_id: str = ""
    entra_client_secret: str = ""
    entra_tenant_id: str = ""
    entra_authority: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    session_expiry_hours: str = "8"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()
