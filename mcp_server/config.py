"""
MCP Server Configuration
Port: 8012
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Server Configuration
    APP_NAME: str = "AutoPro MCP Server"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("MCP_PORT", "8012"))  # Port configurabil, default 8012
    
    # Orchestrator Configuration
    ORCHESTRATOR_URL: str = "http://localhost:3030"
    ORCHESTRATOR_TIMEOUT: int = 300
    
    # API Keys from ENV
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # External Services
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    LINEAR_API_KEY: Optional[str] = os.getenv("LINEAR_API_KEY")
    DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    
    # Authentication
    API_KEY_HEADER: str = "X-API-Key"
    VALID_API_KEYS: list = ["dev-key-12345", "prod-key-67890"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
