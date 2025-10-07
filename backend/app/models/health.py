"""
Pydantic models for health check and status endpoints
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelStatus(BaseModel):
    """Model status information"""
    model_id: str = Field(description="Model identifier")
    loaded: bool = Field(description="Whether model is loaded")
    gpu_memory_used: Optional[int] = Field(None, description="GPU memory used in MB")
    gpu_memory_total: Optional[int] = Field(None, description="Total GPU memory in MB")
    last_loaded: Optional[str] = Field(None, description="Last loaded timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Overall service status")
    version: str = Field(description="Application version")
    uptime: float = Field(description="Service uptime in seconds")
    models: Dict[str, ModelStatus] = Field(description="Model status information")
    gpu_info: Dict[str, Any] = Field(default_factory=dict, description="GPU information")
    system_info: Dict[str, Any] = Field(default_factory=dict, description="System information")
