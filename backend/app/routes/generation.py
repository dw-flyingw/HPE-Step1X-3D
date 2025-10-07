"""
Generation routes for 3D model and image generation
"""

import os
import time
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from ..models.generation import (
    GenerationRequest,
    GenerationResponse,
    TextToImageRequest,
    TextToImageResponse,
    ConvertMeshRequest,
    ConvertMeshResponse,
)
from ..services.model_service import model_service
from ..services.mesh_service import mesh_service
from ..config import settings

router = APIRouter(prefix="/api/v1", tags=["generation"])


@router.post("/text-to-image", response_model=TextToImageResponse)
async def text_to_image(
    prompt: str = Form(...),
    width: int = Form(1024),
    height: int = Form(1024),
    num_inference_steps: int = Form(20),
    guidance_scale: float = Form(7.5),
    seed: Optional[int] = Form(None)
):
    """Generate image from text prompt using Stable Diffusion XL"""
    
    try:
        # Validate parameters
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Generate image
        image_bytes, metadata = await model_service.generate_text_to_image(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        # Save image to output directory
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.png"
        output_path = Path(settings.output_dir) / "models" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        
        return TextToImageResponse(
            success=True,
            filename=filename,
            file_size=len(image_bytes),
            generation_time=metadata["generation_time"],
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-image generation failed: {str(e)}")


@router.post("/generate-3d", response_model=GenerationResponse)
async def generate_3d_from_image(
    image: UploadFile = File(...),
    mode: str = Form("geometry"),
    guidance_scale: float = Form(7.5),
    num_steps: int = Form(50),
    seed: int = Form(2025)
):
    """Generate 3D model from uploaded image"""
    
    try:
        # Validate parameters
        if mode not in ["geometry", "textured"]:
            raise HTTPException(status_code=400, detail="Mode must be 'geometry' or 'textured'")
        
        if not (1.0 <= guidance_scale <= 15.0):
            raise HTTPException(status_code=400, detail="Guidance scale must be between 1.0 and 15.0")
        
        if not (10 <= num_steps <= 100):
            raise HTTPException(status_code=400, detail="Number of steps must be between 10 and 100")
        
        # Read image file
        image_bytes = await image.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Image file is empty")
        
        # Generate 3D model
        model_bytes, metadata = await model_service.generate_3d_from_image(
            image_bytes=image_bytes,
            mode=mode,
            guidance_scale=guidance_scale,
            num_steps=num_steps,
            seed=seed
        )
        
        # Save model to output directory
        timestamp = int(time.time())
        filename = f"{mode}_{seed}_{timestamp}.glb"
        output_path = Path(settings.output_dir) / "models" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(model_bytes)
        
        return GenerationResponse(
            success=True,
            filename=filename,
            file_size=len(model_bytes),
            generation_time=metadata["generation_time"],
            mode=mode,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"3D generation failed: {str(e)}")


@router.post("/convert-mesh", response_model=ConvertMeshResponse)
async def convert_mesh(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    target_format: str = Form("glb"),
    quality: str = Form("high")
):
    """Convert uploaded 3D file to mesh format"""
    
    try:
        # Validate parameters
        if target_format not in ["glb", "obj", "stl", "ply"]:
            raise HTTPException(status_code=400, detail="Target format must be one of: glb, obj, stl, ply")
        
        if quality not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Quality must be one of: low, medium, high")
        
        # Validate file format
        if not mesh_service.validate_format(file.filename, "input"):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported formats: {mesh_service.get_supported_formats()['input']}"
            )
        
        # Read file
        file_bytes = await file.read()
        
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Convert mesh
        converted_bytes, metadata = await mesh_service.convert_to_mesh(
            file_bytes=file_bytes,
            filename=file.filename,
            prompt=prompt,
            target_format=target_format,
            quality=quality
        )
        
        # Save converted file
        timestamp = int(time.time())
        original_name = Path(file.filename).stem
        filename = f"{original_name}_{target_format}_{timestamp}.{target_format}"
        output_path = Path(settings.output_dir) / "models" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(converted_bytes)
        
        return ConvertMeshResponse(
            success=True,
            filename=filename,
            file_size=len(converted_bytes),
            conversion_time=metadata["conversion_time"],
            original_format=metadata["original_format"],
            target_format=target_format,
            mesh_info=metadata["mesh_info"],
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mesh conversion failed: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated file"""
    
    try:
        # Security check - prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = Path(settings.output_dir) / "models" / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type based on file extension
        file_ext = file_path.suffix.lower()
        media_types = {
            ".glb": "model/gltf-binary",
            ".obj": "model/obj",
            ".stl": "model/stl",
            ".ply": "application/octet-stream",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }
        
        media_type = media_types.get(file_ext, "application/octet-stream")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/files")
async def list_generated_files():
    """List all generated files"""
    
    try:
        models_dir = Path(settings.output_dir) / "models"
        
        if not models_dir.exists():
            return {"files": [], "total": 0}
        
        files = []
        for file_path in models_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "extension": file_path.suffix.lower()
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "files": files,
            "total": len(files),
            "directory": str(models_dir)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a generated file"""
    
    try:
        # Security check - prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = Path(settings.output_dir) / "models" / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path.unlink()
        
        return {
            "status": "success",
            "message": f"File {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
