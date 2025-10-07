"""
Pydantic models for generation requests and responses
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """Request model for 3D generation"""
    mode: str = Field("geometry", description="Generation mode: 'geometry' or 'textured'")
    guidance_scale: float = Field(7.5, ge=1.0, le=15.0, description="Guidance scale for generation")
    num_steps: int = Field(50, ge=10, le=100, description="Number of inference steps")
    seed: int = Field(2025, ge=0, le=999999, description="Random seed for reproducibility")


class GenerationResponse(BaseModel):
    """Response model for 3D generation"""
    success: bool = Field(description="Whether generation was successful")
    filename: str = Field(description="Generated filename")
    file_size: int = Field(description="File size in bytes")
    generation_time: float = Field(description="Generation time in seconds")
    mode: str = Field(description="Generation mode used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TextToImageRequest(BaseModel):
    """Request model for text-to-image generation"""
    prompt: str = Field(..., min_length=1, max_length=500, description="Text prompt for image generation")
    width: int = Field(1024, ge=512, le=2048, description="Image width")
    height: int = Field(1024, ge=512, le=2048, description="Image height")
    num_inference_steps: int = Field(20, ge=10, le=50, description="Number of inference steps")
    guidance_scale: float = Field(7.5, ge=1.0, le=20.0, description="Guidance scale")
    seed: Optional[int] = Field(None, ge=0, le=999999, description="Random seed")


class TextToImageResponse(BaseModel):
    """Response model for text-to-image generation"""
    success: bool = Field(description="Whether generation was successful")
    filename: str = Field(description="Generated image filename")
    file_size: int = Field(description="File size in bytes")
    generation_time: float = Field(description="Generation time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConvertMeshRequest(BaseModel):
    """Request model for mesh conversion"""
    prompt: Optional[str] = Field(None, max_length=500, description="Modification prompt")
    target_format: str = Field("glb", description="Target format: glb, obj, stl, ply")
    quality: str = Field("high", description="Conversion quality: low, medium, high")


class ConvertMeshResponse(BaseModel):
    """Response model for mesh conversion"""
    success: bool = Field(description="Whether conversion was successful")
    filename: str = Field(description="Converted filename")
    file_size: int = Field(description="File size in bytes")
    conversion_time: float = Field(description="Conversion time in seconds")
    original_format: str = Field(description="Original file format")
    target_format: str = Field(description="Target file format")
    mesh_info: Dict[str, Any] = Field(default_factory=dict, description="Mesh statistics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
