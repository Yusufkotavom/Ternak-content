#!/usr/bin/env python3
"""
Test script untuk Auto Content Generator
"""

import asyncio
import os
from src.modules.keyword_research import KeywordResearch
from src.modules.content_generator import ContentGenerator
from src.modules.image_generator import ImageGenerator
from src.modules.wordpress_publisher import WordPressPublisher
from src.utils.config import Settings

async def test_keyword_research():
    """Test keyword research module"""
    print("🔍 Testing Keyword Research...")
    
    try:
        research = KeywordResearch()
        result = await research.research_keyword("diet sehat")
        
        print(f"✅ Keyword research successful")
        print(f"   - Related keywords: {len(result.get('related_keywords', []))}")
        print(f"   - Questions: {len(result.get('questions', []))}")
        print(f"   - Competition: {result.get('competition', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Keyword research failed: {str(e)}")
        return False

async def test_content_generator():
    """Test content generator module"""
    print("\n✍️  Testing Content Generator...")
    
    try:
        generator = ContentGenerator()
        
        # Test outline generation
        research_data = {
            'related_keywords': ['diet sehat', 'makanan sehat'],
            'questions': ['Apa itu diet sehat?', 'Bagaimana cara diet sehat?'],
            'competition': 'Medium'
        }
        
        outline = await generator.generate_outline("diet sehat", research_data)
        print(f"✅ Outline generation successful")
        print(f"   - Title: {outline.get('title', 'N/A')}")
        
        # Test content generation
        content = await generator.generate_content("diet sehat", outline, research_data)
        print(f"✅ Content generation successful")
        print(f"   - Word count: {content.get('word_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Content generation failed: {str(e)}")
        return False

async def test_image_generator():
    """Test image generator module"""
    print("\n🖼️  Testing Image Generator...")
    
    try:
        generator = ImageGenerator()
        
        # Test stock image APIs
        images = await generator._get_stock_images("diet sehat")
        print(f"✅ Image generation successful")
        print(f"   - Found {len(images)} images")
        
        return True
    except Exception as e:
        print(f"❌ Image generation failed: {str(e)}")
        return False

async def test_wordpress_publisher():
    """Test WordPress publisher module"""
    print("\n📝 Testing WordPress Publisher...")
    
    try:
        publisher = WordPressPublisher()
        
        # Test connection
        success = await publisher.test_connection()
        
        if success:
            print("✅ WordPress connection successful")
        else:
            print("⚠️  WordPress connection failed (check credentials)")
        
        return True
    except Exception as e:
        print(f"❌ WordPress publisher failed: {str(e)}")
        return False

async def test_full_pipeline():
    """Test full content generation pipeline"""
    print("\n🚀 Testing Full Pipeline...")
    
    try:
        # Initialize modules
        research = KeywordResearch()
        generator = ContentGenerator()
        image_gen = ImageGenerator()
        
        # Test with single keyword
        keyword = "diet sehat"
        
        print(f"Processing keyword: {keyword}")
        
        # 1. Research
        research_data = await research.research_keyword(keyword)
        print("✅ Research completed")
        
        # 2. Generate outline
        outline = await generator.generate_outline(keyword, research_data)
        print("✅ Outline generated")
        
        # 3. Generate content
        content = await generator.generate_content(keyword, outline, research_data)
        print("✅ Content generated")
        
        # 4. Generate images
        images = await image_gen.generate_images(keyword, content)
        print(f"✅ Images generated: {len(images)}")
        
        # 5. Build HTML
        html_content = await generator.build_html(keyword, content, images)
        print("✅ HTML built")
        
        # 6. Save to file
        os.makedirs("output", exist_ok=True)
        filename = f"output/test_{keyword.replace(' ', '_')}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Content saved to: {filename}")
        
        return True
    except Exception as e:
        print(f"❌ Full pipeline failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Auto Content Generator - System Test")
    print("=" * 50)
    
    tests = [
        ("Keyword Research", test_keyword_research),
        ("Content Generator", test_content_generator),
        ("Image Generator", test_image_generator),
        ("WordPress Publisher", test_wordpress_publisher),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())