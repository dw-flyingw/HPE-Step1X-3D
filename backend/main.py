"""
FastAPI Backend for Step1X-3D
Wraps HuggingFace Inference API
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
import base64
import io
import os
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Step1X-3D API")

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/stepfun-ai/Step1X-3D"
HF_TOKEN = os.getenv("HF_TOKEN")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "model": "stepfun-ai/Step1X-3D",
        "hf_token_set": bool(HF_TOKEN)
    }

@app.post("/generate")
async def generate_3d(
    image: UploadFile = File(...),
    mode: str = Form("geometry"),  # "geometry" or "textured"
    guidance_scale: float = Form(7.5),
    num_steps: int = Form(50),
    seed: int = Form(2025)
):
    """
    Generate 3D model from image using HuggingFace Inference API
    
    Args:
        image: Input image file
        mode: "geometry" or "textured"
        guidance_scale: Guidance scale (1-15)
        num_steps: Inference steps (10-100)
        seed: Random seed
    """
    if not HF_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="HF_TOKEN not configured. Set it in .env file"
        )
    
    try:
        # Read and prepare image
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes))
        
        # Resize if too large
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Call HuggingFace Inference API
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": img_b64,
            "parameters": {
                "mode": mode,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_steps,
                "seed": seed
            }
        }
        
        print(f"Calling HF Inference API (mode={mode}, steps={num_steps})...")
        
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            # Save the 3D model
            output_file = OUTPUT_DIR / f"{mode}_{seed}.glb"
            output_file.write_bytes(response.content)
            
            return FileResponse(
                output_file,
                media_type="model/gltf-binary",
                filename=output_file.name
            )
        
        elif response.status_code == 503:
            raise HTTPException(
                status_code=503,
                detail="Model is loading. Please wait 30-60 seconds and try again."
            )
        
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Invalid HF_TOKEN. Check your token in .env file."
            )
        
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"HuggingFace API error: {response.text}"
            )
    
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Request timeout. Try reducing num_steps."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

