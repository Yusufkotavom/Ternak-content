"""
Configuration settings untuk Auto Content Generator
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Image APIs
    unsplash_api_key: Optional[str] = os.getenv("UNSPLASH_API_KEY")
    pixabay_api_key: Optional[str] = os.getenv("PIXABAY_API_KEY")
    pexels_api_key: Optional[str] = os.getenv("PEXELS_API_KEY")
    
    # WordPress Configuration
    wordpress_url: Optional[str] = os.getenv("WORDPRESS_URL")
    wordpress_user: Optional[str] = os.getenv("WORDPRESS_USER")
    wordpress_app_password: Optional[str] = os.getenv("WORDPRESS_APP_PASSWORD")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./content_generator.db")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Content Generation Settings
    default_language: str = "id"
    content_length: int = 1500
    max_images_per_article: int = 3
    
    class Config:
        env_file = ".env"