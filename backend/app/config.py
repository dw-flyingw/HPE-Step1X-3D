"""
Configuration management for the Step1X-3D backend
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # HuggingFace Configuration
    hf_token: Optional[str] = Field(None, env="HF_TOKEN")
    hf_cache_dir: str = Field("./cache", env="HF_CACHE_DIR")
    
    # Backend Configuration
    backend_host: str = Field("0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(8000, env="BACKEND_PORT")
    backend_workers: int = Field(1, env="BACKEND_WORKERS")
    
    # GPU Configuration
    cuda_visible_devices: str = Field("0,1,2,3", env="CUDA_VISIBLE_DEVICES")
    gpu_memory_fraction: float = Field(0.8, env="GPU_MEMORY_FRACTION")
    max_concurrent_requests: int = Field(4, env="MAX_CONCURRENT_REQUESTS")
    
    # Model Configuration
    model_cache_dir: str = Field("./models", env="MODEL_CACHE_DIR")
    step1x3d_model_id: str = Field("stepfun-ai/Step1X-3D", env="STEP1X3D_MODEL_ID")
    sdxl_model_id: str = Field("stabilityai/stable-diffusion-xl-base-1.0", env="SDXL_MODEL_ID")
    
    # Output Configuration
    output_dir: str = Field("./output", env="OUTPUT_DIR")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Development Configuration
    debug: bool = Field(False, env="DEBUG")
    reload: bool = Field(False, env="RELOAD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def gpu_devices(self) -> List[int]:
        """Parse CUDA_VISIBLE_DEVICES into list of integers"""
        try:
            return [int(x.strip()) for x in self.cuda_visible_devices.split(",") if x.strip()]
        except ValueError:
            return [0]  # Default to GPU 0 if parsing fails
    
    @property
    def backend_url(self) -> str:
        """Construct backend URL"""
        return f"http://{self.backend_host}:{self.backend_port}"
    
    def create_directories(self) -> None:
        """Create necessary directories"""
        directories = [
            self.hf_cache_dir,
            self.model_cache_dir,
            self.output_dir,
            os.path.join(self.output_dir, "models"),
            os.path.join(self.output_dir, "logs"),
            os.path.join(self.output_dir, "temp"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Global settings instance
settings = Settings()
