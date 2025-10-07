"""
Step1X-3D Backend - FastAPI Application
Local GPU inference server for 3D model generation
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.routes import generation_router, health_router
from app.services.model_service import model_service
from app.services.gpu_service import gpu_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(settings.output_dir) / "logs" / "backend.log")
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info("Starting Step1X-3D Backend...")
    
    try:
        # Create necessary directories
        settings.create_directories()
        logger.info("Directories created successfully")
        
        # Check GPU availability
        gpu_info = gpu_service.get_gpu_info()
        logger.info(f"GPU Info: {gpu_info}")
        
        # Initialize models in background
        logger.info("Initializing models...")
        await model_service.initialize_models()
        logger.info("Models initialized successfully")
        
        logger.info("Backend startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Step1X-3D Backend...")
    
    try:
        # Clean up model resources
        await model_service.cleanup()
        logger.info("Model cleanup complete")
        
        # Clear GPU cache
        gpu_service.clear_cache()
        logger.info("GPU cache cleared")
        
        logger.info("Backend shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Step1X-3D Backend",
    description="Local GPU inference server for Step1X-3D 3D model generation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health_router)
app.include_router(generation_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "service": "Step1X-3D Backend",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.reload,
        workers=1 if settings.reload else settings.backend_workers,
        log_level=settings.log_level.lower(),
        access_log=True
    )
