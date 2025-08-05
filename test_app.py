"""
Simple test untuk memverifikasi aplikasi berjalan
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_app():
    """Test aplikasi"""
    print("🧪 Testing Auto Content Generator App...")
    
    try:
        # Test imports
        from main import app
        print("✅ App imported successfully")
        
        # Test settings
        from src.utils.config import Settings
        settings = Settings()
        print(f"✅ Settings loaded: {settings.host}:{settings.port}")
        
        # Test modules
        from src.modules.keyword_research import KeywordResearch
        from src.modules.content_generator import ContentGenerator
        from src.modules.image_generator import ImageGenerator
        from src.modules.wordpress_publisher import WordPressPublisher
        
        print("✅ All modules imported successfully")
        
        # Test simple keyword research
        keyword_research = KeywordResearch()
        research_data = await keyword_research.research_keyword("test keyword")
        print(f"✅ Keyword research works: {research_data['keyword']}")
        
        # Test content generation
        content_generator = ContentGenerator()
        outline = await content_generator.generate_outline("test keyword", research_data)
        print(f"✅ Content generation works: {outline.get('title', 'No title')}")
        
        print("\n🎉 All tests passed! App is ready to use.")
        print("\n🚀 To start the app:")
        print("   python run.py")
        print("\n🌐 Then visit: http://localhost:8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_app())