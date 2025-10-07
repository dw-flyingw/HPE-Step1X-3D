"""
GPU management service for handling GPU resources and monitoring
"""

import torch
import psutil
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class GPUService:
    """Service for managing GPU resources"""
    
    def __init__(self):
        self.device = self._get_best_device()
        self.gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        self.memory_fraction = settings.gpu_memory_fraction
        self._memory_cache: Dict[int, Dict[str, Any]] = {}
        
    def _get_best_device(self) -> str:
        """Get the best available device"""
        if torch.cuda.is_available():
            # Use the first available GPU from CUDA_VISIBLE_DEVICES
            available_devices = settings.gpu_devices
            if available_devices and available_devices[0] < torch.cuda.device_count():
                return f"cuda:{available_devices[0]}"
            return "cuda:0"
        return "cpu"
    
    @property
    def is_cuda_available(self) -> bool:
        """Check if CUDA is available"""
        return torch.cuda.is_available()
    
    @property
    def device_name(self) -> str:
        """Get device name"""
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(self.device)
        return "CPU"
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get comprehensive GPU information"""
        if not torch.cuda.is_available():
            return {"available": False, "count": 0}
        
        gpu_info = {
            "available": True,
            "count": self.gpu_count,
            "devices": []
        }
        
        for i in range(self.gpu_count):
            device_info = {
                "index": i,
                "name": torch.cuda.get_device_name(i),
                "memory_total": torch.cuda.get_device_properties(i).total_memory,
                "memory_allocated": torch.cuda.memory_allocated(i),
                "memory_reserved": torch.cuda.memory_reserved(i),
                "memory_free": torch.cuda.get_device_properties(i).total_memory - torch.cuda.memory_allocated(i),
                "utilization": self._get_gpu_utilization(i)
            }
            gpu_info["devices"].append(device_info)
        
        return gpu_info
    
    def _get_gpu_utilization(self, device_id: int) -> float:
        """Get GPU utilization percentage"""
        try:
            # This is a simplified version - in production you might want to use nvidia-ml-py
            return 0.0  # Placeholder
        except Exception:
            return 0.0
    
    def get_memory_usage(self, device_id: Optional[int] = None) -> Dict[str, int]:
        """Get memory usage for a specific device"""
        if not torch.cuda.is_available():
            return {"allocated": 0, "reserved": 0, "total": 0}
        
        if device_id is None:
            device_id = 0
        
        return {
            "allocated": torch.cuda.memory_allocated(device_id),
            "reserved": torch.cuda.memory_reserved(device_id),
            "total": torch.cuda.get_device_properties(device_id).total_memory
        }
    
    @asynccontextmanager
    async def gpu_context(self, device_id: Optional[int] = None):
        """Context manager for GPU operations with memory management"""
        if not torch.cuda.is_available():
            yield "cpu"
            return
        
        if device_id is None:
            device_id = 0
        
        device = f"cuda:{device_id}"
        
        try:
            # Set memory fraction
            torch.cuda.set_per_process_memory_fraction(self.memory_fraction, device_id)
            
            # Clear cache before operation
            torch.cuda.empty_cache()
            
            logger.info(f"Using GPU {device_id} with memory fraction {self.memory_fraction}")
            yield device
            
        finally:
            # Clean up after operation
            torch.cuda.empty_cache()
    
    def clear_cache(self, device_id: Optional[int] = None):
        """Clear GPU memory cache"""
        if torch.cuda.is_available():
            if device_id is None:
                torch.cuda.empty_cache()
            else:
                torch.cuda.empty_cache()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_used_percent": psutil.virtual_memory().percent,
            "python_version": torch.__version__,
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "cudnn_version": torch.backends.cudnn.version() if torch.cuda.is_available() else None,
        }
    
    def is_memory_available(self, required_memory_mb: int, device_id: Optional[int] = None) -> bool:
        """Check if sufficient GPU memory is available"""
        if not torch.cuda.is_available():
            return False
        
        if device_id is None:
            device_id = 0
        
        memory_info = self.get_memory_usage(device_id)
        available_memory = memory_info["total"] - memory_info["reserved"]
        required_bytes = required_memory_mb * 1024 * 1024
        
        return available_memory >= required_bytes


# Global GPU service instance
gpu_service = GPUService()
