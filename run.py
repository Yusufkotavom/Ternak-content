"""
Auto Content Generator - Run Script
Simple script untuk menjalankan aplikasi
Windows compatible
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import Settings

def main():
    """Main function untuk menjalankan aplikasi"""
    print("🚀 Auto Content Generator")
    print("=" * 40)
    
    # Load settings
    settings = Settings()
    
    # Check if running on Windows
    is_windows = settings.is_windows()
    print(f"📍 Platform: {'Windows' if is_windows else 'Linux/Mac'}")
    
    # Validate settings
    if not settings.validate_settings():
        print("❌ Configuration validation failed!")
        print("Please check your .env file and ensure all required directories exist.")
        return
    
    # Show API status
    api_status = settings.get_free_api_status()
    print("\n📊 API Configuration:")
    for api, status in api_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {api}")
    
    # Check if at least one AI API is configured
    if not any([api_status["openai"], api_status["cohere"], api_status["anthropic"], api_status["huggingface"]]):
        print("\n⚠️ Warning: No AI API configured!")
        print("Please configure at least one AI API in your .env file:")
        print("  - OpenAI API Key")
        print("  - Cohere API Key")
        print("  - Anthropic API Key")
        print("  - HuggingFace Token")
        print("\nYou can get free API keys from:")
        print("  - Cohere: https://cohere.ai/ (Free tier available)")
        print("  - Anthropic: https://anthropic.com/ (Free tier available)")
        print("  - HuggingFace: https://huggingface.co/ (Free)")
    
    # Create necessary directories
    directories = ["output", "output/images", "templates", "static"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory ready: {directory}")
    
    # Start the server
    print(f"\n🌐 Starting server on http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Debug mode: {settings.debug}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()