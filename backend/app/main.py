from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from .routers import rag
from .models.schemas import HealthResponse
from .config import settings

# Create FastAPI app
app = FastAPI(
    title="Mini-RAG API",
    description="A personal knowledge base management system using RAG (Retrieval-Augmented Generation)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])

# Mount static files and templates for frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    templates = Jinja2Templates(directory=os.path.join(frontend_path, "templates"))
else:
    templates = None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main page."""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("""
        <html>
            <head><title>Mini-RAG API</title></head>
            <body>
                <h1>Mini-RAG API</h1>
                <p>Welcome to the Mini-RAG API. Visit <a href="/docs">/docs</a> for API documentation.</p>
                <p>Frontend templates not found. Please check the frontend directory structure.</p>
            </body>
        </html>
        """)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚀 Mini-RAG API starting up...")
    print(f"📁 Data directory: {settings.data_dir}")
    print(f"📤 Uploads directory: {settings.uploads_dir}")
    print(f"🔍 Document store directory: {settings.vectorstore_dir}")
    print(f"🤖 AI Model: {settings.azure_ai_model_name}")
    
    # Create directories if they don't exist
    os.makedirs(settings.uploads_dir, exist_ok=True)
    os.makedirs(settings.vectorstore_dir, exist_ok=True)
    
    print("✅ Mini-RAG API startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Mini-RAG API shutting down...")
    print("✅ Cleanup complete!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )