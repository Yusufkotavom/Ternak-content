#!/usr/bin/env python3
"""
Auto Content Generator with E-E-A-T + Bulk Keyword Input
Main application entry point
"""

import os
import asyncio
from typing import List, Dict, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
import uvicorn
from dotenv import load_dotenv

from src.modules.keyword_research import KeywordResearch
from src.modules.content_generator import ContentGenerator
from src.modules.image_generator import ImageGenerator
from src.modules.wordpress_publisher import WordPressPublisher
from src.utils.config import Settings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Auto Content Generator",
    description="Sistem otomatisasi content generation dengan E-E-A-T",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize settings
settings = Settings()

# Initialize modules
keyword_research = KeywordResearch()
content_generator = ContentGenerator()
image_generator = ImageGenerator()
wordpress_publisher = WordPressPublisher()

class KeywordRequest(BaseModel):
    keywords: List[str]
    language: str = "id"
    content_type: str = "article"

class ContentResponse(BaseModel):
    keyword: str
    title: str
    content: str
    images: List[str]
    status: str

@app.get("/", response_class=HTMLResponse)
async def home(request):
    """Homepage dengan form input keyword"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-keywords")
async def upload_keywords(file: UploadFile = File(...)):
    """Upload file CSV dengan keywords"""
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
            keywords = df['keyword'].tolist() if 'keyword' in df.columns else df.iloc[:, 0].tolist()
        else:
            raise HTTPException(status_code=400, detail="File harus berformat CSV")
        
        return {"keywords": keywords, "count": len(keywords)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error membaca file: {str(e)}")

@app.post("/process-keywords")
async def process_keywords(request: KeywordRequest):
    """Proses bulk keywords untuk riset dan generate content"""
    results = []
    
    for keyword in request.keywords:
        try:
            # 1. Keyword Research
            research_data = await keyword_research.research_keyword(keyword)
            
            # 2. Generate Content Outline
            outline = await content_generator.generate_outline(keyword, research_data)
            
            # 3. Generate Full Content with E-E-A-T
            content = await content_generator.generate_content(keyword, outline, research_data)
            
            # 4. Generate Images
            images = await image_generator.generate_images(keyword, content)
            
            # 5. Build HTML
            html_content = await content_generator.build_html(keyword, content, images)
            
            results.append(ContentResponse(
                keyword=keyword,
                title=content.get('title', ''),
                content=html_content,
                images=images,
                status="success"
            ))
            
        except Exception as e:
            results.append(ContentResponse(
                keyword=keyword,
                title="",
                content="",
                images=[],
                status=f"error: {str(e)}"
            ))
    
    return {"results": results}

@app.post("/publish-wordpress")
async def publish_to_wordpress(keyword: str, content: str):
    """Publish content ke WordPress"""
    try:
        result = await wordpress_publisher.publish_post(keyword, content)
        return {"status": "success", "post_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )