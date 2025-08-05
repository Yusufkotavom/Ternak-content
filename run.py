#!/usr/bin/env python3
"""
Simple run script untuk Auto Content Generator
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Auto Content Generator...")
    print("📱 Web Interface: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )