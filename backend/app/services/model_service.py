"""
Model service for handling Step1X-3D and SDXL model inference
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import torch
from PIL import Image
import io
import base64

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from diffusers import StableDiffusionXLPipeline, DiffusionPipeline
import accelerate

from ..config import settings
from .gpu_service import gpu_service

logger = logging.getLogger(__name__)


class ModelService:
    """Service for managing and running model inference"""
    
    def __init__(self):
        self.step1x3d_pipeline: Optional[Any] = None
        self.sdxl_pipeline: Optional[StableDiffusionXLPipeline] = None
        self.models_loaded = False
        self._loading_lock = asyncio.Lock()
        
    async def initialize_models(self) -> None:
        """Initialize all models"""
        async with self._loading_lock:
            if self.models_loaded:
                return
            
            logger.info("Initializing models...")
            
            try:
                # Load SDXL pipeline first (smaller, faster to load)
                await self._load_sdxl_pipeline()
                
                # Load Step1X-3D pipeline
                await self._load_step1x3d_pipeline()
                
                self.models_loaded = True
                logger.info("All models loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize models: {e}")
                raise
    
    async def _load_sdxl_pipeline(self) -> None:
        """Load Stable Diffusion XL pipeline"""
        logger.info("Loading SDXL pipeline...")
        
        async with gpu_service.gpu_context():
            try:
                self.sdxl_pipeline = StableDiffusionXLPipeline.from_pretrained(
                    settings.sdxl_model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    cache_dir=settings.model_cache_dir,
                    local_files_only=False,
                )
                
                # Enable memory efficient attention
                self.sdxl_pipeline.enable_model_cpu_offload()
                self.sdxl_pipeline.enable_vae_slicing()
                
                logger.info("SDXL pipeline loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load SDXL pipeline: {e}")
                raise
    
    async def _load_step1x3d_pipeline(self) -> None:
        """Load Step1X-3D pipeline"""
        logger.info("Loading Step1X-3D pipeline...")
        
        async with gpu_service.gpu_context():
            try:
                # Note: This is a placeholder - actual Step1X-3D loading will depend on the model format
                # The actual implementation will depend on how the model is provided
                
                # For now, we'll use a placeholder that matches the expected interface
                self.step1x3d_pipeline = {
                    "model_id": settings.step1x3d_model_id,
                    "loaded": True,
                    "device": gpu_service.device
                }
                
                logger.info("Step1X-3D pipeline loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load Step1X-3D pipeline: {e}")
                raise
    
    async def generate_text_to_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Generate image from text prompt"""
        
        if not self.models_loaded:
            await self.initialize_models()
        
        if self.sdxl_pipeline is None:
            raise RuntimeError("SDXL pipeline not loaded")
        
        start_time = time.time()
        
        try:
            async with gpu_service.gpu_context():
                # Set seed if provided
                if seed is not None:
                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed(seed)
                
                # Generate image
                result = self.sdxl_pipeline(
                    prompt=prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=torch.Generator(device=gpu_service.device).manual_seed(seed) if seed else None,
                )
                
                # Convert to bytes
                image = result.images[0]
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                
                generation_time = time.time() - start_time
                
                metadata = {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed,
                    "generation_time": generation_time,
                    "device": gpu_service.device,
                }
                
                return img_bytes.getvalue(), metadata
                
        except Exception as e:
            logger.error(f"Text-to-image generation failed: {e}")
            raise
    
    async def generate_3d_from_image(
        self,
        image_bytes: bytes,
        mode: str = "geometry",
        guidance_scale: float = 7.5,
        num_steps: int = 50,
        seed: int = 2025
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Generate 3D model from image"""
        
        if not self.models_loaded:
            await self.initialize_models()
        
        if self.step1x3d_pipeline is None:
            raise RuntimeError("Step1X-3D pipeline not loaded")
        
        start_time = time.time()
        
        try:
            async with gpu_service.gpu_context():
                # Load and preprocess image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Resize if necessary
                max_size = 1024
                if max(image.size) > max_size:
                    ratio = max_size / max(image.size)
                    new_size = tuple(int(dim * ratio) for dim in image.size)
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convert to base64 for model input
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Placeholder for actual Step1X-3D inference
                # This will be replaced with actual model inference
                # For now, we'll create a dummy GLB file
                dummy_glb = self._create_dummy_glb()
                
                generation_time = time.time() - start_time
                
                metadata = {
                    "mode": mode,
                    "guidance_scale": guidance_scale,
                    "num_steps": num_steps,
                    "seed": seed,
                    "generation_time": generation_time,
                    "device": gpu_service.device,
                    "image_size": image.size,
                }
                
                return dummy_glb, metadata
                
        except Exception as e:
            logger.error(f"3D generation failed: {e}")
            raise
    
    def _create_dummy_glb(self) -> bytes:
        """Create a dummy GLB file for testing"""
        # This is a minimal GLB file structure
        # In production, this would be replaced with actual Step1X-3D output
        dummy_content = b'\x67\x6C\x54\x46\x02\x00\x00\x00'  # GLB header
        dummy_content += b'\x00' * 100  # Add some dummy data
        return dummy_content
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of loaded models"""
        return {
            "step1x3d": {
                "model_id": settings.step1x3d_model_id,
                "loaded": self.step1x3d_pipeline is not None,
                "device": gpu_service.device if self.step1x3d_pipeline else None,
            },
            "sdxl": {
                "model_id": settings.sdxl_model_id,
                "loaded": self.sdxl_pipeline is not None,
                "device": gpu_service.device if self.sdxl_pipeline else None,
            },
            "models_loaded": self.models_loaded,
        }
    
    async def cleanup(self) -> None:
        """Clean up model resources"""
        if self.sdxl_pipeline is not None:
            del self.sdxl_pipeline
            self.sdxl_pipeline = None
        
        if self.step1x3d_pipeline is not None:
            del self.step1x3d_pipeline
            self.step1x3d_pipeline = None
        
        self.models_loaded = False
        gpu_service.clear_cache()


# Global model service instance
model_service = ModelService()
