"""
Mesh processing service for 3D model conversion and manipulation
"""

import tempfile
import os
import time
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

import trimesh
import nibabel as nib
import numpy as np
from skimage import measure

from ..config import settings

logger = logging.getLogger(__name__)


class MeshService:
    """Service for mesh processing and conversion"""
    
    def __init__(self):
        self.supported_formats = {
            'input': ['.glb', '.obj', '.nii.gz'],
            'output': ['.glb', '.obj', '.stl', '.ply']
        }
    
    async def convert_to_mesh(
        self,
        file_bytes: bytes,
        filename: str,
        prompt: Optional[str] = None,
        target_format: str = "glb",
        quality: str = "high"
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Convert uploaded file to mesh format"""
        
        start_time = time.time()
        file_ext = Path(filename).suffix.lower()
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            
            # Load based on file type
            mesh = await self._load_mesh(tmp_path, file_ext)
            
            # Apply modifications if prompt provided
            if prompt:
                mesh = await self._apply_modifications(mesh, prompt)
            
            # Convert to target format
            output_bytes = await self._export_mesh(mesh, target_format, quality)
            
            # Get mesh information
            mesh_info = self._get_mesh_info(mesh)
            
            conversion_time = time.time() - start_time
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            metadata = {
                "original_format": file_ext[1:],  # Remove the dot
                "target_format": target_format,
                "conversion_time": conversion_time,
                "mesh_info": mesh_info,
                "modification_prompt": prompt,
                "quality": quality,
            }
            
            return output_bytes, metadata
            
        except Exception as e:
            logger.error(f"Mesh conversion failed: {e}")
            # Clean up temp file in case of error
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    
    async def _load_mesh(self, file_path: str, file_ext: str) -> trimesh.Trimesh:
        """Load mesh from file based on extension"""
        
        if file_ext in ['.glb', '.obj']:
            return trimesh.load(file_path)
        
        elif file_ext == '.gz' and file_path.endswith('.nii.gz'):
            # Load NIfTI medical imaging file
            return await self._load_nifti_as_mesh(file_path)
        
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    async def _load_nifti_as_mesh(self, file_path: str) -> trimesh.Trimesh:
        """Load NIfTI file and convert to mesh using marching cubes"""
        
        nii_img = nib.load(file_path)
        data = nii_img.get_fdata()
        
        # Normalize data
        data = (data - data.min()) / (data.max() - data.min())
        
        # Use marching cubes to create mesh
        threshold = data.mean() + data.std()
        verts, faces, normals, values = measure.marching_cubes(
            data, 
            threshold,
            spacing=nii_img.header.get_zooms()[:3]  # Use actual voxel spacing
        )
        
        # Create trimesh object
        mesh = trimesh.Trimesh(
            vertices=verts, 
            faces=faces, 
            vertex_normals=normals
        )
        
        return mesh
    
    async def _apply_modifications(self, mesh: trimesh.Trimesh, prompt: str) -> trimesh.Trimesh:
        """Apply modifications to mesh based on prompt"""
        
        # This is a placeholder for actual mesh modification logic
        # In a real implementation, this might involve:
        # - Text-to-mesh modification using AI models
        # - Procedural modifications based on prompt keywords
        # - Style transfer or texture application
        
        logger.info(f"Applying modifications based on prompt: {prompt}")
        
        # For now, we'll just return the original mesh
        # In production, this would apply actual modifications
        return mesh
    
    async def _export_mesh(
        self, 
        mesh: trimesh.Trimesh, 
        target_format: str, 
        quality: str = "high"
    ) -> bytes:
        """Export mesh to target format"""
        
        # Configure export settings based on quality
        export_kwargs = {}
        
        if target_format == 'glb':
            export_kwargs = {
                'file_type': 'glb',
                'binary': True
            }
        elif target_format == 'obj':
            export_kwargs = {
                'file_type': 'obj'
            }
        elif target_format == 'stl':
            export_kwargs = {
                'file_type': 'stl',
                'binary': True
            }
        elif target_format == 'ply':
            export_kwargs = {
                'file_type': 'ply',
                'binary': True
            }
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        # Export to bytes
        output = mesh.export(**export_kwargs)
        
        if isinstance(output, str):
            return output.encode('utf-8')
        else:
            return output
    
    def _get_mesh_info(self, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """Get comprehensive mesh information"""
        
        info = {
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
            "edges": len(mesh.edges),
            "is_watertight": mesh.is_watertight,
            "is_winding_consistent": mesh.is_winding_consistent,
            "is_empty": mesh.is_empty,
            "has_vertex_normals": mesh.vertex_normals is not None,
            "has_face_normals": mesh.face_normals is not None,
            "has_visual": mesh.visual is not None,
            "volume": float(mesh.volume) if hasattr(mesh, 'volume') else None,
            "surface_area": float(mesh.surface_area) if hasattr(mesh, 'surface_area') else None,
        }
        
        # Add bounding box information
        if hasattr(mesh, 'bounds'):
            bounds = mesh.bounds
            info["bounding_box"] = {
                "min": bounds[0].tolist(),
                "max": bounds[1].tolist(),
                "size": (bounds[1] - bounds[0]).tolist()
            }
        
        # Add center of mass
        if hasattr(mesh, 'center_mass'):
            info["center_mass"] = mesh.center_mass.tolist()
        
        # Add visual information
        if mesh.visual is not None:
            visual_info = {}
            
            if hasattr(mesh.visual, 'material'):
                visual_info["has_material"] = mesh.visual.material is not None
            
            if hasattr(mesh.visual, 'vertex_colors'):
                visual_info["has_vertex_colors"] = mesh.visual.vertex_colors is not None
            
            if hasattr(mesh.visual, 'face_colors'):
                visual_info["has_face_colors"] = mesh.visual.face_colors is not None
            
            info["visual"] = visual_info
        
        return info
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Get supported input and output formats"""
        return self.supported_formats.copy()
    
    def validate_format(self, filename: str, format_type: str = "input") -> bool:
        """Validate if file format is supported"""
        if format_type not in self.supported_formats:
            return False
        
        file_ext = Path(filename).suffix.lower()
        
        # Handle special case for .nii.gz
        if filename.endswith('.nii.gz'):
            file_ext = '.nii.gz'
        
        return file_ext in self.supported_formats[format_type]


# Global mesh service instance
mesh_service = MeshService()
