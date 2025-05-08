"""Main application module for the AI Support Agent."""
import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config.config import get_config, ensure_directories_exist
from .api.routes import router as api_router

# Load environment variables
load_dotenv()

# Get configuration
config = get_config()

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Handle application startup and shutdown events.
    
    Args:
        app: The FastAPI application
        
    Yields:
        None
    """
    # Startup
    print("Starting up AI Support Agent")
    
    # Ensure directories exist
    ensure_directories_exist()
    
    yield
    
    # Shutdown
    print("Shutting down AI Support Agent")

# Create FastAPI app
app = FastAPI(
    title="AI Support Agent",
    description="AI-driven customer support system for product information and comparison",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(api_router)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint to verify the API is running.
    
    Returns:
        JSONResponse: Response with status message
    """
    return JSONResponse(
        content={"message": "AI Support Agent API is running"},
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 