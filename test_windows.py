"""
Windows Test Script
Quick test untuk memastikan aplikasi berjalan di Windows
"""

import os
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test semua import yang diperlukan"""
    print("🔧 Testing imports...")
    
    try:
        # Test basic imports
        import fastapi
        import uvicorn
        import pandas
        import requests
        import aiohttp
        print("✅ Basic imports successful")
        
        # Test AI imports
        try:
            import openai
            print("✅ OpenAI import successful")
        except ImportError:
            print("⚠️ OpenAI not installed (optional)")
        
        try:
            import cohere
            print("✅ Cohere import successful")
        except ImportError:
            print("⚠️ Cohere not installed (optional)")
        
        try:
            import anthropic
            print("✅ Anthropic import successful")
        except ImportError:
            print("⚠️ Anthropic not installed (optional)")
        
        try:
            from transformers import pipeline
            print("✅ Transformers import successful")
        except ImportError:
            print("⚠️ Transformers not installed (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def test_directories():
    """Test pembuatan direktori"""
    print("\n📁 Testing directories...")
    
    try:
        directories = ["output", "output/images", "templates", "static"]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if os.path.exists(directory):
                print(f"✅ Directory created: {directory}")
            else:
                print(f"❌ Failed to create: {directory}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Directory test failed: {str(e)}")
        return False

def test_config():
    """Test konfigurasi"""
    print("\n⚙️ Testing configuration...")
    
    try:
        # Add src to path
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from src.utils.config import Settings
        
        settings = Settings()
        
        # Test basic settings
        print(f"✅ Host: {settings.host}")
        print(f"✅ Port: {settings.port}")
        print(f"✅ Debug: {settings.debug}")
        print(f"✅ Platform: {'Windows' if settings.is_windows() else 'Linux/Mac'}")
        
        # Test API status
        api_status = settings.get_free_api_status()
        print("📊 API Status:")
        for api, status in api_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {api}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_modules():
    """Test modul-modul utama"""
    print("\n🔧 Testing modules...")
    
    try:
        # Add src to path
        sys.path.append(str(Path(__file__).parent / "src"))
        
        # Test module imports
        from src.modules.keyword_research import KeywordResearch
        from src.modules.content_generator import ContentGenerator
        from src.modules.image_generator import ImageGenerator
        from src.modules.wordpress_publisher import WordPressPublisher
        
        print("✅ All modules imported successfully")
        
        # Test module initialization
        keyword_research = KeywordResearch()
        content_generator = ContentGenerator()
        image_generator = ImageGenerator()
        wordpress_publisher = WordPressPublisher()
        
        print("✅ All modules initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Module test failed: {str(e)}")
        return False

async def test_async_functions():
    """Test fungsi async"""
    print("\n⚡ Testing async functions...")
    
    try:
        # Add src to path
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from src.modules.keyword_research import KeywordResearch
        
        keyword_research = KeywordResearch()
        
        # Test simple async function
        research_data = await keyword_research.research_keyword("test keyword")
        
        print("✅ Async function test successful")
        return True
        
    except Exception as e:
        print(f"❌ Async function test failed: {str(e)}")
        return False

def test_file_operations():
    """Test operasi file"""
    print("\n📄 Testing file operations...")
    
    try:
        # Test file writing
        test_file = "output/test_file.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Test content")
        
        # Test file reading
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content == "Test content":
            print("✅ File operations successful")
            
            # Clean up
            os.remove(test_file)
            return True
        else:
            print("❌ File content mismatch")
            return False
        
    except Exception as e:
        print(f"❌ File operations test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Windows Compatibility Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Directories", test_directories),
        ("Configuration", test_config),
        ("Modules", test_modules),
        ("File Operations", test_file_operations)
    ]
    
    results = {}
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Run async test
    try:
        async_result = asyncio.run(test_async_functions())
        results["Async Functions"] = async_result
    except Exception as e:
        print(f"❌ Async Functions test crashed: {str(e)}")
        results["Async Functions"] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! App is ready for Windows.")
        print("\n🚀 To start the app, run:")
        print("   python run.py")
        print("\n🧪 To run full system tests:")
        print("   python test_system.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return results

if __name__ == "__main__":
    main()