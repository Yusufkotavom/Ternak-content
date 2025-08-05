"""
Auto Content Generator - Main Application
FastAPI application untuk content generation dengan E-E-A-T
Windows compatible with free AI APIs
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import Settings
from src.modules.keyword_research import KeywordResearch
from src.modules.content_generator import ContentGenerator
from src.modules.image_generator import ImageGenerator
from src.modules.wordpress_publisher import WordPressPublisher

# Initialize FastAPI app
app = FastAPI(
    title="Auto Content Generator",
    description="Generate content dengan E-E-A-T menggunakan AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load settings
settings = Settings()

# Initialize modules
keyword_research = KeywordResearch()
content_generator = ContentGenerator()
image_generator = ImageGenerator()
wordpress_publisher = WordPressPublisher()

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Create output directory
os.makedirs("output", exist_ok=True)
os.makedirs("output/images", exist_ok=True)

# Pydantic models
from pydantic import BaseModel

class KeywordRequest(BaseModel):
    keywords: List[str]
    language: str = "id"
    content_type: str = "article"
    word_count: int = 1500
    generate_images: bool = True
    publish_to_wordpress: bool = False

class ContentResponse(BaseModel):
    keyword: str
    research_data: Dict
    content: Dict
    images: List[str]
    html_content: str
    status: str

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Auto Content Generator...")
    
    # Validate settings
    if not settings.validate_settings():
        print("❌ Configuration validation failed!")
        return
    
    # Check API status
    api_status = settings.get_free_api_status()
    print("📊 API Status:")
    for api, status in api_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {api}")
    
    print("✅ Application started successfully!")
    print(f"🌐 Web interface: http://{settings.host}:{settings.port}")
    print(f"📚 API docs: http://{settings.host}:{settings.port}/docs")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage dengan form input keyword"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "apis": settings.get_free_api_status()
    }

@app.post("/upload-keywords")
async def upload_keywords(file: UploadFile = File(...)):
    """Upload file CSV dengan keywords"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File harus berformat CSV")
        
        # Read CSV file
        import pandas as pd
        import io
        
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Extract keywords
        if 'keyword' in df.columns:
            keywords = df['keyword'].dropna().tolist()
        else:
            keywords = df.iloc[:, 0].dropna().tolist()
        
        return {
            "status": "success",
            "keywords": keywords,
            "count": len(keywords)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/process-keywords")
async def process_keywords(request: KeywordRequest):
    """Proses bulk keywords untuk riset dan generate content"""
    try:
        results = []
        
        for keyword in request.keywords[:settings.max_keywords_per_batch]:
            try:
                print(f"🔍 Processing keyword: {keyword}")
                
                # 1. Research keyword
                research_data = await keyword_research.research_keyword(keyword)
                
                # 2. Generate content outline
                outline = await content_generator.generate_outline(keyword, research_data)
                
                # 3. Generate full content
                content = await content_generator.generate_content(keyword, outline, research_data)
                
                # 4. Generate images (if enabled)
                images = []
                if request.generate_images:
                    images = await image_generator.generate_images(keyword, content)
                
                # 5. Build HTML content
                html_content = await content_generator.build_html(keyword, content, images)
                
                # 6. Save HTML file
                html_filename = f"{keyword.replace(' ', '_')}_{int(time.time())}.html"
                html_path = os.path.join("output", html_filename)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # 7. Publish to WordPress (if enabled)
                wordpress_post_id = None
                if request.publish_to_wordpress and settings.wordpress_url:
                    wordpress_post_id = await wordpress_publisher.publish_post(
                        keyword, html_content, content.get('title', keyword)
                    )
                
                result = ContentResponse(
                    keyword=keyword,
                    research_data=research_data,
                    content=content,
                    images=images,
                    html_content=html_content,
                    status="success"
                )
                
                results.append(result.dict())
                
                print(f"✅ Completed: {keyword}")
                
            except Exception as e:
                print(f"❌ Error processing {keyword}: {str(e)}")
                results.append({
                    "keyword": keyword,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "results": results,
            "total_processed": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing keywords: {str(e)}")

@app.post("/publish-wordpress")
async def publish_to_wordpress(keyword: str = Form(...), content: str = Form(...)):
    """Publish content ke WordPress"""
    try:
        if not settings.wordpress_url:
            raise HTTPException(status_code=400, detail="WordPress URL not configured")
        
        post_id = await wordpress_publisher.publish_post(keyword, content)
        
        return {
            "status": "success",
            "post_id": post_id,
            "wordpress_url": settings.wordpress_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing to WordPress: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Get application status and API configuration"""
    return {
        "status": "running",
        "version": "1.0.0",
        "apis": settings.get_free_api_status(),
        "settings": {
            "content_length": settings.content_length,
            "max_images": settings.max_images_per_article,
            "language": settings.language,
            "output_dir": settings.output_dir
        }
    }

@app.get("/api/test-ai")
async def test_ai_apis():
    """Test AI APIs"""
    test_results = {}
    
    # Test OpenAI
    if settings.openai_api_key:
        try:
            import openai
            openai.api_key = settings.openai_api_key
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            test_results["openai"] = "✅ Working"
        except Exception as e:
            test_results["openai"] = f"❌ Error: {str(e)}"
    else:
        test_results["openai"] = "❌ Not configured"
    
    # Test Cohere
    if settings.cohere_api_key:
        try:
            import cohere
            co = cohere.Client(settings.cohere_api_key)
            response = co.generate(
                model="command",
                prompt="Hello",
                max_tokens=10
            )
            test_results["cohere"] = "✅ Working"
        except Exception as e:
            test_results["cohere"] = f"❌ Error: {str(e)}"
    else:
        test_results["cohere"] = "❌ Not configured"
    
    # Test Anthropic
    if settings.anthropic_api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model="claude-instant-1.2",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            test_results["anthropic"] = "✅ Working"
        except Exception as e:
            test_results["anthropic"] = f"❌ Error: {str(e)}"
    else:
        test_results["anthropic"] = "❌ Not configured"
    
    return test_results

if __name__ == "__main__":
    import time
    
    print("🚀 Starting Auto Content Generator...")
    print(f"📍 Platform: {'Windows' if settings.is_windows() else 'Linux/Mac'}")
    print(f"🔧 Debug mode: {settings.debug}")
    
    # Validate settings before starting
    if not settings.validate_settings():
        print("❌ Configuration validation failed! Please check your .env file.")
        sys.exit(1)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )