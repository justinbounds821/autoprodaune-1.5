"""
Configuration management for AutoPro Daune API.

This module provides centralized configuration management using Pydantic settings
with environment variable support and validation.
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=False, description="Debug mode")
    SECRET_KEY: str = Field(default="dev-secret-key", description="Secret key for JWT tokens")
    
    # Database
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase anon key")
    DATABASE_URL: Optional[str] = Field(default=None, description="Direct database URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    
    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", description="API version prefix")
    PROJECT_NAME: str = Field(default="AutoPro Daune API", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")
    
    # CORS
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3006,http://localhost:8001",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # WhatsApp
    WHATSAPP_ACCESS_TOKEN: str = Field(default="", description="WhatsApp Business API access token")
    WHATSAPP_PHONE_NUMBER_ID: str = Field(default="", description="WhatsApp Business phone number ID")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = Field(default="", description="WhatsApp webhook verification token")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.2, description="Sentry traces sample rate")
    SENTRY_PROFILES_SAMPLE_RATE: float = Field(default=0.0, description="Sentry profiles sample rate")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=5, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    RATE_LIMIT_RPM: int = Field(default=120, description="Rate limit requests per minute")
    
    # Automation
    AUTOMATION_ENABLED: bool = Field(default=True, description="Enable automation scheduler")
    
    # File Storage
    CLOUDFLARE_R2_ACCESS_KEY_ID: str = Field(default="", description="Cloudflare R2 access key ID")
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: str = Field(default="", description="Cloudflare R2 secret access key")
    CLOUDFLARE_R2_BUCKET_NAME: str = Field(default="", description="Cloudflare R2 bucket name")
    CLOUDFLARE_R2_ENDPOINT_URL: str = Field(default="", description="Cloudflare R2 endpoint URL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Convenience function for backward compatibility
def get_config() -> Settings:
    """Get application configuration (alias for get_settings)."""
    return get_settings()
