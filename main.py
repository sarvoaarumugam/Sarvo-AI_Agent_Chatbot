

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

# Import configuration
from src.agents.config import Config, validate_config

# Import routers (API endpoints)
from src.endpoints.chat_router import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Startup: Runs when server starts
    Shutdown: Runs when server stops
    """
    # ===== STARTUP =====
    print("\n" + "="*60)
    print("🚀 SARVO AI AGENT CHATBOT - STARTING UP")
    print("="*60)
    
    # Validate configuration
    if not validate_config():
        print("⚠️  Configuration issues detected. Some features may not work.")
    
    # Create necessary directories
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    # Initialize the agent (pre-warm)
    print("🤖 Pre-warming AI agent...")
    from src.agents.master_agent import get_master_agent
    get_master_agent()
    
    yield  # Server is running
    
    # ===== SHUTDOWN =====
    print("\n🛑 Shutting down Sarvo AI...")
    print("👋 Goodbye!\n")



app = FastAPI(
    title="Sarvo AI Agent Chatbot",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================== MIDDLEWARE ====================

# CORS - Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(chat_router)



@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """
    ❤️ Health check endpoint.
    
    Use this to verify the server is running.
    """
    return {
        "status": "healthy",
        "service": "Sarvo AI Agent Chatbot",
        "version": "1.0.0"
    }


@app.get("/info")
async def get_info():
    """
    ℹ️ Get system information.
    """
    return {
        "name": "Sarvo AI Agent Chatbot",
        "version": "1.0.0",
        "capabilities": [
            "chat",
            "image_generation",
            "image_editing", 
            "web_search"
        ],
        "models": {
            "chat": Config.CHAT_MODEL,
            "image": Config.IMAGE_MODEL
        },
        "endpoints": {
            "chat": "POST /api/chat",
            "upload": "POST /api/upload",
            "history": "GET /api/history",
            "clear": "POST /api/clear",
            "files": "GET /api/files"
        }
    }


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting Sarvo AI Agent Chatbot Server...")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,  # Auto-reload on code changes
        log_level="info"
    )