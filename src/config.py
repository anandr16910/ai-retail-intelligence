"""Configuration management for AI Retail Intelligence Platform."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Settings
    app_name: str = "AI Retail Intelligence Platform"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    
    # Data Settings
    data_dir: str = Field(default="data", description="Data directory path")
    model_dir: str = Field(default="models", description="Model directory path")
    
    # ML Model Settings
    default_forecast_horizon: int = Field(default=30, description="Default forecast horizon in days")
    confidence_level: float = Field(default=0.95, description="Confidence level for predictions")
    
    # LLM Settings
    llm_model_name: str = Field(default="mock", description="LLM model name")
    llm_max_tokens: int = Field(default=1000, description="Maximum tokens for LLM responses")
    
    # AWS Settings (optional)
    aws_region: Optional[str] = Field(default=None, description="AWS region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret key")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()