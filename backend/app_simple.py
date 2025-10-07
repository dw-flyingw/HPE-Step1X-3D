"""
Simplified Step1X-3D Backend using official pipelines
Much simpler and more maintainable than the custom implementation
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import torch
from tempfile import NamedTemporaryFile
import os
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Import official Step1X-3D pipelines
from step1x3d_geometry.models.pipelines.pipeline import Step1X3DGeometryPipeline
from step1x3d_texture.pipelines.step1x_3d_texture_synthesis_pipeline import Step1X3DTexturePipeline
from step1x3d_geometry.models.pipelines.pipeline_utils import reduce_face, remove_degenerate_face

app = FastAPI(title="Step1X-3D API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure output directory
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global variables for pipelines (loaded once on startup)
geometry_pipeline = None
texture_pipeline = None


@app.on_event("startup")
async def load_models():
    """Load models once on startup"""
    global geometry_pipeline, texture_pipeline
    
    print("Loading Step1X-3D Geometry Pipeline...")
    geometry_pipeline = Step1X3DGeometryPipeline.from_pretrained(
        "stepfun-ai/Step1X-3D", 
        subfolder='Step1X-3D-Geometry-1300m'
    ).to("cuda")
    print("✅ Geometry pipeline loaded")
    
    print("Loading Step1X-3D Texture Pipeline...")
    texture_pipeline = Step1X3DTexturePipeline.from_pretrained(
        "stepfun-ai/Step1X-3D", 
        subfolder="Step1X-3D-Texture"
    )
    print("✅ Texture pipeline loaded")
    
    print("🚀 Step1X-3D API ready!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "model": "Step1X-3D",
        "geometry_loaded": geometry_pipeline is not None,
        "texture_loaded": texture_pipeline is not None
    }


@app.post("/generate-geometry")
async def generate_geometry(
    image: UploadFile = File(...),
    guidance_scale: float = Form(7.5),
    num_inference_steps: int = Form(50),
    seed: int = Form(2025)
):
    """
    Generate 3D geometry from an input image.
    Returns an untextured .glb mesh file.
    """
    if geometry_pipeline is None:
        return {"error": "Geometry pipeline not loaded"}, 503
    
    # Save uploaded image temporarily
    image_data = await image.read()
    image_pil = Image.open(io.BytesIO(image_data))
    
    with NamedTemporaryFile(delete=False, suffix=".png", dir=OUTPUT_DIR) as tmp_img:
        image_pil.save(tmp_img.name)
        input_image_path = tmp_img.name
    
    try:
        # Generate geometry using official pipeline
        generator = torch.Generator(device=geometry_pipeline.device).manual_seed(seed)
        out = geometry_pipeline(
            input_image_path,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator
        )
        
        # Export untextured mesh
        with NamedTemporaryFile(delete=False, suffix=".glb", dir=OUTPUT_DIR) as tmp_mesh:
            out.mesh[0].export(tmp_mesh.name)
            mesh_path = tmp_mesh.name
        
        return FileResponse(
            mesh_path,
            media_type="model/gltf-binary",
            filename=f"geometry_{seed}.glb"
        )
    
    finally:
        # Clean up temporary input image
        if os.path.exists(input_image_path):
            os.remove(input_image_path)


@app.post("/generate-textured")
async def generate_textured(
    image: UploadFile = File(...),
    guidance_scale: float = Form(7.5),
    num_inference_steps: int = Form(50),
    seed: int = Form(2025)
):
    """
    Generate a fully textured 3D asset from an input image.
    Returns a textured .glb mesh file.
    """
    if geometry_pipeline is None or texture_pipeline is None:
        return {"error": "Pipelines not loaded"}, 503
    
    # Save uploaded image temporarily
    image_data = await image.read()
    image_pil = Image.open(io.BytesIO(image_data))
    
    with NamedTemporaryFile(delete=False, suffix=".png", dir=OUTPUT_DIR) as tmp_img:
        image_pil.save(tmp_img.name)
        input_image_path = tmp_img.name
    
    try:
        # Stage 1: Generate geometry
        print("Stage 1: Generating geometry...")
        generator = torch.Generator(device=geometry_pipeline.device).manual_seed(seed)
        out = geometry_pipeline(
            input_image_path,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator
        )
        
        # Get untextured mesh
        untextured_mesh = out.mesh[0]
        
        # Stage 2: Add texture
        print("Stage 2: Generating texture...")
        # Preprocess mesh
        untextured_mesh = remove_degenerate_face(untextured_mesh)
        untextured_mesh = reduce_face(untextured_mesh)
        
        # Generate texture
        textured_mesh = texture_pipeline(input_image_path, untextured_mesh)
        
        # Export textured mesh
        with NamedTemporaryFile(delete=False, suffix=".glb", dir=OUTPUT_DIR) as tmp_mesh:
            textured_mesh.export(tmp_mesh.name)
            mesh_path = tmp_mesh.name
        
        return FileResponse(
            mesh_path,
            media_type="model/gltf-binary",
            filename=f"textured_{seed}.glb"
        )
    
    finally:
        # Clean up temporary input image
        if os.path.exists(input_image_path):
            os.remove(input_image_path)


@app.post("/generate-3d")
async def generate_3d_legacy(prompt: str = Form(...)):
    """
    Legacy endpoint for backward compatibility.
    Note: Step1X-3D works with images, not text prompts.
    This endpoint will return an error message.
    """
    return {
        "error": "Step1X-3D requires image input, not text prompts",
        "hint": "Use /generate-geometry or /generate-textured with an image file",
        "example": "curl -X POST http://localhost:8000/generate-textured -F 'image=@input.png'"
    }

