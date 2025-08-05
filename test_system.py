"""
Test System untuk Auto Content Generator
Test semua modul dan fitur
Windows compatible
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import Settings
from src.modules.keyword_research import KeywordResearch
from src.modules.content_generator import ContentGenerator
from src.modules.image_generator import ImageGenerator
from src.modules.wordpress_publisher import WordPressPublisher

class SystemTester:
    def __init__(self):
        self.settings = Settings()
        self.keyword_research = KeywordResearch()
        self.content_generator = ContentGenerator()
        self.image_generator = ImageGenerator()
        self.wordpress_publisher = WordPressPublisher()
        
        # Test data
        self.test_keyword = "tips menurunkan berat badan"
        self.test_keywords = [
            "diet sehat",
            "tips menurunkan berat badan",
            "makanan tinggi protein"
        ]
    
    async def test_configuration(self):
        """Test konfigurasi aplikasi"""
        print("🔧 Testing Configuration...")
        
        try:
            # Validate settings
            if not self.settings.validate_settings():
                print("❌ Configuration validation failed!")
                return False
            
            # Check API status
            api_status = self.settings.get_free_api_status()
            print("📊 API Status:")
            for api, status in api_status.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {api}")
            
            # Check directories
            directories = ["output", "templates", "static"]
            for directory in directories:
                if os.path.exists(directory):
                    print(f"✅ Directory exists: {directory}")
                else:
                    print(f"❌ Directory missing: {directory}")
            
            print("✅ Configuration test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {str(e)}")
            return False
    
    async def test_keyword_research(self):
        """Test keyword research module"""
        print("\n🔍 Testing Keyword Research...")
        
        try:
            # Test single keyword research
            research_data = await self.keyword_research.research_keyword(self.test_keyword)
            
            print(f"✅ Keyword: {research_data['keyword']}")
            print(f"✅ Related keywords: {len(research_data.get('related_keywords', []))}")
            print(f"✅ Questions: {len(research_data.get('questions', []))}")
            print(f"✅ Competition: {research_data.get('competition', {}).get('level', 'Unknown')}")
            print(f"✅ Search volume: {research_data.get('search_volume', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Keyword research test failed: {str(e)}")
            return False
    
    async def test_content_generation(self):
        """Test content generation module"""
        print("\n✍️ Testing Content Generation...")
        
        try:
            # Test outline generation
            research_data = await self.keyword_research.research_keyword(self.test_keyword)
            outline = await self.content_generator.generate_outline(self.test_keyword, research_data)
            
            print(f"✅ Outline generated: {outline.get('title', 'No title')}")
            print(f"✅ H2 sections: {len(outline.get('h2_sections', []))}")
            print(f"✅ FAQ count: {len(outline.get('faq', []))}")
            
            # Test full content generation
            content = await self.content_generator.generate_content(self.test_keyword, outline, research_data)
            
            print(f"✅ Content generated: {content.get('title', 'No title')}")
            print(f"✅ Word count: {content.get('word_count', 0)}")
            print(f"✅ Keywords: {len(content.get('keywords', []))}")
            
            return True
            
        except Exception as e:
            print(f"❌ Content generation test failed: {str(e)}")
            return False
    
    async def test_image_generation(self):
        """Test image generation module"""
        print("\n🖼️ Testing Image Generation...")
        
        try:
            # Test image generation
            content = {"title": "Test Content", "content": "Test content for image generation"}
            images = await self.image_generator.generate_images(self.test_keyword, content)
            
            print(f"✅ Images generated: {len(images)}")
            for i, image in enumerate(images):
                print(f"  📷 Image {i+1}: {image}")
            
            return True
            
        except Exception as e:
            print(f"❌ Image generation test failed: {str(e)}")
            return False
    
    async def test_wordpress_publisher(self):
        """Test WordPress publisher module"""
        print("\n📝 Testing WordPress Publisher...")
        
        try:
            # Test connection
            if self.settings.wordpress_url:
                connection_status = await self.wordpress_publisher.test_connection()
                print(f"✅ WordPress connection: {connection_status}")
            else:
                print("⚠️ WordPress not configured, skipping test")
            
            return True
            
        except Exception as e:
            print(f"❌ WordPress publisher test failed: {str(e)}")
            return False
    
    async def test_full_pipeline(self):
        """Test full content generation pipeline"""
        print("\n🚀 Testing Full Pipeline...")
        
        try:
            results = []
            
            for keyword in self.test_keywords[:2]:  # Test first 2 keywords
                print(f"\n📝 Processing: {keyword}")
                
                # 1. Research
                research_data = await self.keyword_research.research_keyword(keyword)
                print(f"  ✅ Research completed")
                
                # 2. Generate outline
                outline = await self.content_generator.generate_outline(keyword, research_data)
                print(f"  ✅ Outline generated")
                
                # 3. Generate content
                content = await self.content_generator.generate_content(keyword, outline, research_data)
                print(f"  ✅ Content generated ({content.get('word_count', 0)} words)")
                
                # 4. Generate images
                images = await self.image_generator.generate_images(keyword, content)
                print(f"  ✅ Images generated ({len(images)} images)")
                
                # 5. Build HTML
                html_content = await self.content_generator.build_html(keyword, content, images)
                print(f"  ✅ HTML built")
                
                # 6. Save to file
                filename = f"test_{keyword.replace(' ', '_')}.html"
                filepath = os.path.join("output", filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"  ✅ Saved to: {filepath}")
                
                results.append({
                    "keyword": keyword,
                    "word_count": content.get('word_count', 0),
                    "images": len(images),
                    "file": filepath
                })
            
            print(f"\n✅ Full pipeline test completed!")
            print("📊 Results:")
            for result in results:
                print(f"  📝 {result['keyword']}: {result['word_count']} words, {result['images']} images")
            
            return True
            
        except Exception as e:
            print(f"❌ Full pipeline test failed: {str(e)}")
            return False
    
    async def test_ai_apis(self):
        """Test AI APIs"""
        print("\n🤖 Testing AI APIs...")
        
        try:
            # Test OpenAI
            if self.settings.openai_api_key:
                try:
                    import openai
                    openai.api_key = self.settings.openai_api_key
                    response = await openai.ChatCompletion.acreate(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=10
                    )
                    print("✅ OpenAI: Working")
                except Exception as e:
                    print(f"❌ OpenAI: {str(e)}")
            else:
                print("⚠️ OpenAI: Not configured")
            
            # Test Cohere
            if self.settings.cohere_api_key:
                try:
                    import cohere
                    co = cohere.Client(self.settings.cohere_api_key)
                    response = co.generate(
                        model="command",
                        prompt="Hello",
                        max_tokens=10
                    )
                    print("✅ Cohere: Working")
                except Exception as e:
                    print(f"❌ Cohere: {str(e)}")
            else:
                print("⚠️ Cohere: Not configured")
            
            # Test Anthropic
            if self.settings.anthropic_api_key:
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
                    response = client.messages.create(
                        model="claude-instant-1.2",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Hello"}]
                    )
                    print("✅ Anthropic: Working")
                except Exception as e:
                    print(f"❌ Anthropic: {str(e)}")
            else:
                print("⚠️ Anthropic: Not configured")
            
            return True
            
        except Exception as e:
            print(f"❌ AI APIs test failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run semua test"""
        print("🧪 Starting System Tests...")
        print("=" * 50)
        
        tests = [
            ("Configuration", self.test_configuration),
            ("AI APIs", self.test_ai_apis),
            ("Keyword Research", self.test_keyword_research),
            ("Content Generation", self.test_content_generation),
            ("Image Generation", self.test_image_generation),
            ("WordPress Publisher", self.test_wordpress_publisher),
            ("Full Pipeline", self.test_full_pipeline)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} test crashed: {str(e)}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready to use.")
        else:
            print("⚠️ Some tests failed. Please check the configuration.")
        
        return results

async def main():
    """Main test function"""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Run tests
    asyncio.run(main())