"""
Health check and status routes
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models.health import HealthResponse, ModelStatus
from ..services.gpu_service import gpu_service
from ..services.model_service import model_service
from ..config import settings

router = APIRouter(prefix="/health", tags=["health"])

# Store startup time for uptime calculation
startup_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    try:
        # Get model status
        model_status = model_service.get_model_status()
        
        # Get GPU information
        gpu_info = gpu_service.get_gpu_info()
        
        # Get system information
        system_info = gpu_service.get_system_info()
        
        # Calculate uptime
        uptime = time.time() - startup_time
        
        # Build model status dict
        models = {}
        for model_name, status in model_status.items():
            if model_name != "models_loaded":
                models[model_name] = ModelStatus(
                    model_id=status["model_id"],
                    loaded=status["loaded"],
                    gpu_memory_used=gpu_info.get("devices", [{}])[0].get("memory_allocated") if gpu_info.get("devices") else None,
                    gpu_memory_total=gpu_info.get("devices", [{}])[0].get("memory_total") if gpu_info.get("devices") else None,
                    last_loaded=None  # TODO: Track when models were loaded
                )
        
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            uptime=uptime,
            models=models,
            gpu_info=gpu_info,
            system_info=system_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/models")
async def get_model_status():
    """Get detailed model status"""
    
    try:
        model_status = model_service.get_model_status()
        gpu_info = gpu_service.get_gpu_info()
        
        return {
            "models": model_status,
            "gpu_info": gpu_info,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")


@router.get("/gpu")
async def get_gpu_status():
    """Get GPU status and utilization"""
    
    try:
        gpu_info = gpu_service.get_gpu_info()
        
        return {
            "gpu_info": gpu_info,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get GPU status: {str(e)}")


@router.post("/models/load")
async def load_models():
    """Manually trigger model loading"""
    
    try:
        await model_service.initialize_models()
        
        return {
            "status": "success",
            "message": "Models loaded successfully",
            "models": model_service.get_model_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load models: {str(e)}")


@router.post("/gpu/clear-cache")
async def clear_gpu_cache():
    """Clear GPU memory cache"""
    
    try:
        gpu_service.clear_cache()
        
        return {
            "status": "success",
            "message": "GPU cache cleared",
            "gpu_info": gpu_service.get_gpu_info()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear GPU cache: {str(e)}")
