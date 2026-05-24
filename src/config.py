"""
Application Configuration Module

Loads settings from environment variables with validation via Pydantic.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""

    # ========== Application Settings ==========
    APP_NAME: str = "Context-Aware Question Generator"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # ========== FastAPI Settings ==========
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_TITLE: str = "Context-Aware Question Generation API"
    API_VERSION: str = "0.1.0"

    # ========== Storage Settings ==========
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")

    # ========== MCP Configuration ==========
    MCP_CONFIG_PATH: str = os.getenv("MCP_CONFIG_PATH", "mcp.json")

    # ========== LLM Provider Keys ==========
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # ========== Confluence Settings ==========
    CONFLUENCE_API_URL: Optional[str] = os.getenv("CONFLUENCE_API_URL")
    CONFLUENCE_API_KEY: Optional[str] = os.getenv("CONFLUENCE_API_KEY")

    # ========== Jira Settings ==========
    JIRA_API_URL: Optional[str] = os.getenv("JIRA_API_URL")
    JIRA_API_KEY: Optional[str] = os.getenv("JIRA_API_KEY")

    # ========== Salesforce Settings ==========
    SALESFORCE_INSTANCE_URL: Optional[str] = os.getenv("SALESFORCE_INSTANCE_URL")
    SALESFORCE_CLIENT_ID: Optional[str] = os.getenv("SALESFORCE_CLIENT_ID")
    SALESFORCE_CLIENT_SECRET: Optional[str] = os.getenv("SALESFORCE_CLIENT_SECRET")
    SALESFORCE_USERNAME: Optional[str] = os.getenv("SALESFORCE_USERNAME")
    SALESFORCE_SECURITY_TOKEN: Optional[str] = os.getenv("SALESFORCE_SECURITY_TOKEN")

    # ========== HubSpot Settings ==========
    HUBSPOT_API_KEY: Optional[str] = os.getenv("HUBSPOT_API_KEY")

    # ========== GitHub Settings (Optional) ==========
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_ORG: Optional[str] = os.getenv("GITHUB_ORG")

    # ========== Custom ERP Settings (Optional) ==========
    ERP_API_URL: Optional[str] = os.getenv("ERP_API_URL")
    ERP_API_KEY: Optional[str] = os.getenv("ERP_API_KEY")

    # ========== Wiki Settings (Optional) ==========
    WIKI_GRAPHQL_URL: Optional[str] = os.getenv("WIKI_GRAPHQL_URL")
    WIKI_API_KEY: Optional[str] = os.getenv("WIKI_API_KEY")

    # ========== Logging Settings ==========
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields


# Singleton instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings singleton"""
    return settings
