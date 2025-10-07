"""
Minimal Gradio Interface for Step1X-3D
Imports only what's needed for inference, avoiding data/training modules
"""

import gradio as gr
import torch
from PIL import Image
import sys
import os

# Add Step1X-3D to path
sys.path.insert(0, "/home/hpadmin/HPE-Step1X-3D/Step1X-3D")
sys.path.insert(0, os.path.join(os.getcwd(), "Step1X-3D"))

# Import ONLY the pipeline module directly, skip __init__.py
import importlib.util

def load_pipeline_module():
    """Load pipeline module directly without going through __init__.py"""
    pipeline_path = os.path.join(
        os.getcwd(), 
        "Step1X-3D/step1x3d_geometry/models/pipelines/pipeline.py"
    )
    
    spec = importlib.util.spec_from_file_location("pipeline", pipeline_path)
    pipeline_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline_module)
    
    return pipeline_module.Step1X3DGeometryPipeline

print("🚀 Loading Step1X-3D pipeline (bypassing data modules)...")

try:
    Step1X3DGeometryPipeline = load_pipeline_module()
    print("✅ Pipeline module loaded")
except Exception as e:
    print(f"❌ Failed to load pipeline: {e}")
    print("\nTrying alternative approach...")
    
    # Alternative: Use HuggingFace Spaces API
    print("💡 Recommendation: Use HuggingFace Spaces instead")
    print("   Visit: https://huggingface.co/spaces/stepfun-ai/Step1X-3D")
    sys.exit(1)

# Global pipeline
geometry_pipeline = None

def load_models():
    """Load models once at startup"""
    global geometry_pipeline
    
    print("Loading Step1X-3D Geometry Pipeline...")
    try:
        geometry_pipeline = Step1X3DGeometryPipeline.from_pretrained(
            "stepfun-ai/Step1X-3D", 
            subfolder='Step1X-3D-Geometry-1300m'
        ).to("cuda")
        print("✅ Geometry pipeline loaded")
    except Exception as e:
        print(f"❌ Failed to load models: {e}")
        print("\nThis might be due to:")
        print("1. Missing model files")
        print("2. Insufficient GPU memory")
        print("3. Network issues downloading models")
        return False
    
    return True

def generate_geometry(image, guidance_scale, num_steps, seed):
    """Generate untextured 3D geometry from image"""
    if geometry_pipeline is None:
        return None, "❌ Error: Model not loaded"
    
    try:
        # Save uploaded image
        if isinstance(image, str):
            image_path = image
        else:
            image_path = "/tmp/input.png"
            image.save(image_path)
        
        # Generate geometry
        generator = torch.Generator(device=geometry_pipeline.device).manual_seed(int(seed))
        out = geometry_pipeline(
            image_path,
            guidance_scale=guidance_scale,
            num_inference_steps=int(num_steps),
            generator=generator
        )
        
        # Export mesh
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"geometry_{seed}.glb")
        out.mesh[0].export(output_path)
        
        return output_path, f"✅ Generated mesh (seed: {seed})"
    
    except Exception as e:
        import traceback
        error_msg = f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        return None, error_msg

# Try to load models
print("\n" + "="*50)
print("Starting model loading...")
print("="*50 + "\n")

if not load_models():
    print("\n❌ Failed to initialize. Using fallback UI...")
    
    # Create fallback UI that explains the issue
    with gr.Blocks(title="Step1X-3D - Setup Required") as demo:
        gr.Markdown("""
        # ⚠️ Step1X-3D Setup Issue
        
        The Step1X-3D repository has dependencies on training/data modules that aren't needed for inference.
        
        ## Recommended Solutions:
        
        ### Option 1: Use HuggingFace Space (Easiest)
        Access the official demo: [stepfun-ai/Step1X-3D](https://huggingface.co/spaces/stepfun-ai/Step1X-3D)
        
        ### Option 2: Install ALL dependencies
        ```bash
        pip install mosaicml-streaming objaverse opencv-python
        ```
        
        ### Option 3: Use HuggingFace Inference API
        ```python
        from huggingface_hub import InferenceClient
        client = InferenceClient()
        result = client.predict("stepfun-ai/Step1X-3D", inputs=image)
        ```
        
        ## Why This Happened
        The Step1X-3D codebase includes training code that imports data loaders (Objaverse, streaming datasets)
        even though we only need the inference pipeline.
        """)
else:
    # Create working UI
    print("✅ Models loaded successfully!")
    
    with gr.Blocks(title="Step1X-3D: Image to 3D") as demo:
        gr.Markdown("""
        # Step1X-3D: Image to 3D Generation
        
        Upload an image to generate a 3D model.
        """)
        
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="filepath", label="Input Image")
                guidance_scale = gr.Slider(1, 15, value=7.5, label="Guidance Scale")
                num_steps = gr.Slider(10, 100, value=50, step=10, label="Inference Steps")
                seed = gr.Number(value=2025, label="Random Seed")
                generate_btn = gr.Button("Generate 3D Model", variant="primary")
            
            with gr.Column():
                output_file = gr.File(label="Download 3D Model (.glb)")
                status_text = gr.Textbox(label="Status", lines=3)
        
        generate_btn.click(
            fn=generate_geometry,
            inputs=[image_input, guidance_scale, num_steps, seed],
            outputs=[output_file, status_text]
        )
        
        gr.Markdown("""
        ### Tips
        - Use clear, well-lit images
        - Higher steps = better quality but slower
        - Generation takes 30-60 seconds
        """)

# Launch
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

