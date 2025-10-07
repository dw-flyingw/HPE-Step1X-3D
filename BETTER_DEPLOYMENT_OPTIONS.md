# Better Deployment Options for Step1X-3D

## The Problem

We've been trying to self-host the **entire Step1X-3D repository**, which includes:
- ❌ Training code and dependencies
- ❌ Data loading utilities (Objaverse, etc.)
- ❌ Evaluation code
- ❌ Many dependencies we don't need for inference

This causes endless dependency issues because we're loading modules meant for training, not just inference.

## Better Options (Ranked by Ease)

### Option 1: Hugging Face Inference Endpoints (EASIEST) ⭐

**Use Hugging Face's managed service** - no Docker, no dependencies, fully managed.

**Pros:**
- ✅ Zero setup - just click and deploy
- ✅ Fully managed infrastructure
- ✅ Auto-scaling
- ✅ No dependency hell
- ✅ Pay per use

**Cons:**
- 💰 Costs money (but likely cheaper than your time debugging)

**How to:**
1. Go to [huggingface.co/inference-endpoints](https://huggingface.co/inference-endpoints)
2. Select `stepfun-ai/Step1X-3D`
3. Choose GPU instance
4. Deploy
5. Get API endpoint URL
6. Use it from your frontend

**Cost:** ~$0.60/hour for GPU inference (only when running)

**Example:**
```python
import requests

API_URL = "https://your-endpoint.endpoints.huggingface.cloud"
headers = {"Authorization": "Bearer YOUR_HF_TOKEN"}

def query(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()
```

---

### Option 2: Use Existing Hugging Face Space (FREE)

**Use the official demo** or fork an existing Space.

**Official Space:** [stepfun-ai/Step1X-3D](https://huggingface.co/spaces/stepfun-ai/Step1X-3D)

**Other Spaces using Step1X-3D:**
- ginigen/3D-LLAMA
- cavargas10/Step1X-TextureGeneration
- minhtung/Step1X-3D

**Pros:**
- ✅ Completely free
- ✅ Already working
- ✅ Can fork and customize
- ✅ No setup needed

**Cons:**
- ⚠️ Shared resources (slower)
- ⚠️ Public usage
- ⚠️ Limited control

**How to:**
1. Go to [official space](https://huggingface.co/spaces/stepfun-ai/Step1X-3D)
2. Use the web UI directly
3. Or fork it and customize
4. Or call it via API

---

### Option 3: Gradio App (RECOMMENDED for self-hosted)

**Use Gradio** - much simpler than FastAPI for ML models.

**Why Gradio:**
- ✅ Built for ML models
- ✅ Auto-generates UI
- ✅ Less code
- ✅ Handles file uploads easily
- ✅ Built-in queueing
- ✅ Can share easily

**Simple Gradio Implementation:**

```python
# app_gradio.py
import gradio as gr
import torch
from step1x3d_geometry.models.pipelines.pipeline import Step1X3DGeometryPipeline

# Load model once
geometry_pipeline = Step1X3DGeometryPipeline.from_pretrained(
    "stepfun-ai/Step1X-3D", 
    subfolder='Step1X-3D-Geometry-1300m'
).to("cuda")

def generate_3d(image, guidance_scale, num_steps):
    """Generate 3D model from image"""
    out = geometry_pipeline(
        image, 
        guidance_scale=guidance_scale,
        num_inference_steps=num_steps
    )
    # Save and return mesh
    mesh_path = "output.glb"
    out.mesh[0].export(mesh_path)
    return mesh_path

# Create Gradio interface
demo = gr.Interface(
    fn=generate_3d,
    inputs=[
        gr.Image(type="filepath", label="Input Image"),
        gr.Slider(1, 15, value=7.5, label="Guidance Scale"),
        gr.Slider(10, 100, value=50, step=10, label="Inference Steps")
    ],
    outputs=gr.File(label="Download 3D Model"),
    title="Step1X-3D: Image to 3D",
    description="Generate 3D models from images using Step1X-3D"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

**Deployment:**
```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip git
RUN pip3 install gradio torch transformers diffusers

WORKDIR /app
COPY app_gradio.py .
RUN git clone https://github.com/stepfun-ai/Step1X-3D.git

CMD ["python3", "app_gradio.py"]
```

---

### Option 4: Inference-Only Container (Current Approach Fixed)

**If you must use FastAPI**, here's the minimal approach:

**Key insight:** Don't import the full step1x3d_geometry library. Use only the pipeline.

```python
# Minimal inference-only backend
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import torch
import sys
import os

# Add Step1X-3D to path
sys.path.insert(0, "/app/Step1X-3D")

# Import ONLY what we need for inference
from step1x3d_geometry.models.pipelines.pipeline import Step1X3DGeometryPipeline

app = FastAPI()

# Load model on startup
@app.on_event("startup")
async def load_model():
    global pipeline
    pipeline = Step1X3DGeometryPipeline.from_pretrained(
        "stepfun-ai/Step1X-3D",
        subfolder="Step1X-3D-Geometry-1300m"
    ).to("cuda")

@app.post("/generate")
async def generate(image: UploadFile = File(...)):
    # Save temp image
    image_path = f"/tmp/{image.filename}"
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    # Generate
    out = pipeline(image_path)
    
    # Export
    mesh_path = "/tmp/output.glb"
    out.mesh[0].export(mesh_path)
    
    return FileResponse(mesh_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Minimal requirements.txt:**
```
fastapi
uvicorn
torch
transformers
diffusers
pillow
python-multipart
```

---

## Recommendation

**For your use case (HPE project):**

1. **Quick proof-of-concept:** Use Option 1 (HF Inference Endpoints)
   - Deploy in 5 minutes
   - Test everything works
   - No debugging needed

2. **Long-term self-hosted:** Use Option 3 (Gradio)
   - Simpler than FastAPI for ML
   - Auto-generates UI
   - Easier maintenance

3. **Custom API needed:** Use Option 4 (Minimal FastAPI)
   - But with the simplified approach above
   - Import ONLY pipeline code
   - Avoid loading data/training modules

## Why Current Approach Failed

The Step1X-3D repository structure:
```
Step1X-3D/
├── step1x3d_geometry/
│   ├── data/          # ← Training data loaders (Objaverse, etc.)
│   ├── models/        # ← Model definitions
│   ├── systems/       # ← Training systems
│   └── utils/         # ← Utilities
└── step1x3d_texture/  # ← Texture synthesis
```

When you `from step1x3d_geometry import ...`, Python loads **everything**, including:
- Data loaders (need cv2, objaverse, etc.)
- Training systems (need wandb, lightning, etc.)
- Evaluation code (need more deps)

**Solution:** Import ONLY the pipeline module, not the whole package.

## Next Steps

Choose an option above and I'll help you implement it properly. My recommendation:

1. Try Option 1 first (HF Inference Endpoints) - 5 min setup
2. If you need self-hosted, go with Option 3 (Gradio) - much simpler
3. Only if you need custom REST API, use Option 4 (minimal FastAPI)

Stop fighting with dependencies - use the right tool for the job! 🎯

