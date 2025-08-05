"""
Configuration Module
Load settings dari environment variables dan .env file
Windows compatible
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Free AI APIs
    cohere_api_key: Optional[str] = os.getenv("COHERE_API_KEY", "")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    huggingface_token: Optional[str] = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Image APIs
    unsplash_api_key: Optional[str] = os.getenv("UNSPLASH_API_KEY", "")
    pixabay_api_key: Optional[str] = os.getenv("PIXABAY_API_KEY", "")
    pexels_api_key: Optional[str] = os.getenv("PEXELS_API_KEY", "")
    
    # WordPress Configuration
    wordpress_url: Optional[str] = os.getenv("WORDPRESS_URL", "")
    wordpress_user: Optional[str] = os.getenv("WORDPRESS_USER", "")
    wordpress_app_password: Optional[str] = os.getenv("WORDPRESS_APP_PASSWORD", "")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./content_generator.db")
    
    # Redis Configuration (for Celery)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Content Generation Settings
    content_length: int = int(os.getenv("CONTENT_LENGTH", "1500"))
    max_images_per_article: int = int(os.getenv("MAX_IMAGES_PER_ARTICLE", "3"))
    language: str = os.getenv("LANGUAGE", "id")
    
    # File Paths (Windows compatible)
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    templates_dir: str = os.getenv("TEMPLATES_DIR", "templates")
    static_dir: str = os.getenv("STATIC_DIR", "static")
    
    # Rate Limiting
    max_requests_per_minute: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    allowed_hosts: list = os.getenv("ALLOWED_HOSTS", "*").split(",")
    
    # Free API Limits
    cohere_free_limit: int = int(os.getenv("COHERE_FREE_LIMIT", "100"))
    anthropic_free_limit: int = int(os.getenv("ANTHROPIC_FREE_LIMIT", "100"))
    huggingface_free_limit: int = int(os.getenv("HUGGINGFACE_FREE_LIMIT", "100"))
    
    # Image Generation Settings
    image_width: int = int(os.getenv("IMAGE_WIDTH", "800"))
    image_height: int = int(os.getenv("IMAGE_HEIGHT", "600"))
    image_quality: int = int(os.getenv("IMAGE_QUALITY", "85"))
    
    # Keyword Research Settings
    max_keywords_per_batch: int = int(os.getenv("MAX_KEYWORDS_PER_BATCH", "50"))
    research_timeout: int = int(os.getenv("RESEARCH_TIMEOUT", "30"))
    
    # Content Settings
    min_content_length: int = int(os.getenv("MIN_CONTENT_LENGTH", "500"))
    max_content_length: int = int(os.getenv("MAX_CONTENT_LENGTH", "3000"))
    
    # E-E-A-T Settings
    enable_eeat: bool = os.getenv("ENABLE_EEAT", "True").lower() == "true"
    eeat_expertise_weight: float = float(os.getenv("EEAT_EXPERTISE_WEIGHT", "0.3"))
    eeat_experience_weight: float = float(os.getenv("EEAT_EXPERIENCE_WEIGHT", "0.3"))
    eeat_authority_weight: float = float(os.getenv("EEAT_AUTHORITY_WEIGHT", "0.2"))
    eeat_trust_weight: float = float(os.getenv("EEAT_TRUST_WEIGHT", "0.2"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.database_url.startswith("sqlite"):
            # Ensure SQLite path is Windows compatible
            db_path = self.database_url.replace("sqlite:///", "")
            if not db_path.startswith("/"):
                # Relative path
                return f"sqlite:///{os.path.join(os.getcwd(), db_path)}"
        return self.database_url
    
    def get_output_path(self, filename: str) -> str:
        """Get output file path (Windows compatible)"""
        return os.path.join(self.output_dir, filename)
    
    def get_template_path(self, template_name: str) -> str:
        """Get template file path (Windows compatible)"""
        return os.path.join(self.templates_dir, template_name)
    
    def get_static_path(self, static_file: str) -> str:
        """Get static file path (Windows compatible)"""
        return os.path.join(self.static_dir, static_file)
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return os.name == 'nt'
    
    def get_user_agent(self) -> str:
        """Get appropriate user agent for the platform"""
        if self.is_windows():
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        else:
            return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    def validate_settings(self) -> bool:
        """Validate required settings"""
        errors = []
        
        # Check if at least one AI API is configured
        if not any([
            self.openai_api_key,
            self.cohere_api_key,
            self.anthropic_api_key,
            self.huggingface_token
        ]):
            errors.append("At least one AI API key is required (OpenAI, Cohere, Anthropic, or HuggingFace)")
        
        # Check output directory
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        # Check templates directory
        if not os.path.exists(self.templates_dir):
            errors.append(f"Templates directory not found: {self.templates_dir}")
        
        # Check static directory
        if not os.path.exists(self.static_dir):
            errors.append(f"Static directory not found: {self.static_dir}")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_free_api_status(self) -> dict:
        """Get status of free API configurations"""
        return {
            "openai": bool(self.openai_api_key),
            "cohere": bool(self.cohere_api_key),
            "anthropic": bool(self.anthropic_api_key),
            "huggingface": bool(self.huggingface_token),
            "unsplash": bool(self.unsplash_api_key),
            "pixabay": bool(self.pixabay_api_key),
            "pexels": bool(self.pexels_api_key)
        }