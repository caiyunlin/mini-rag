#!/usr/bin/env python3
"""
Mini-RAG Application Startup Script
"""
import uvicorn
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app
from backend.app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Mini-RAG Application...")
    print(f"📍 Server will run on: http://{settings.app_host}:{settings.app_port}")
    print(f"📚 API Documentation: http://{settings.app_host}:{settings.app_port}/docs")
    print(f"🔧 Debug mode: {settings.debug}")
    
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level="info"
    )