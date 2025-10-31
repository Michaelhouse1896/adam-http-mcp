"""Configuration management for ADAM MCP Server."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration settings for the ADAM MCP server."""

    # ADAM API Settings
    ADAM_API_TOKEN: str = os.getenv("ADAM_API_TOKEN", "")
    ADAM_BASE_URL: str = os.getenv("ADAM_BASE_URL", "")  # Full URL to ADAM API (e.g., "https://yourschool.adam.co.za/api")

    # MCP Server Settings
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "ADAM School MIS")
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.ADAM_API_TOKEN:
            raise ValueError("ADAM_API_TOKEN is not set in .env file")
        if not cls.ADAM_BASE_URL:
            raise ValueError("ADAM_BASE_URL is not set in .env file")

        # Validate token format (should be 30 characters)
        if len(cls.ADAM_API_TOKEN) != 30:
            raise ValueError("ADAM_API_TOKEN should be 30 characters long")

        # Validate URL format
        if not cls.ADAM_BASE_URL.startswith(("http://", "https://")):
            raise ValueError("ADAM_BASE_URL must start with http:// or https://")

    @classmethod
    def get_auth_header(cls) -> dict[str, str]:
        """Get the authorization header for ADAM API requests."""
        return {"Authorization": f"Bearer {cls.ADAM_API_TOKEN}"}


# Validate configuration on module import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please ensure .env file exists with ADAM_API_TOKEN and ADAM_BASE_URL set")
