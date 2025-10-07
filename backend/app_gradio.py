"""
Step1X-3D Gradio Interface
Much simpler than FastAPI for ML inference
"""

import gradio as gr
import torch
from PIL import Image
import sys
import os

# Add Step1X-3D to Python path
sys.path.insert(0, "/app/Step1X-3D")

# Import only what we need
from step1x3d_geometry.models.pipelines.pipeline import Step1X3DGeometryPipeline
from step1x3d_texture.pipelines.step1x_3d_texture_synthesis_pipeline import Step1X3DTexturePipeline
from step1x3d_geometry.models.pipelines.pipeline_utils import reduce_face, remove_degenerate_face

# Global pipelines
geometry_pipeline = None
texture_pipeline = None


def load_models():
    """Load models once at startup"""
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


def generate_geometry(image, guidance_scale, num_steps, seed):
    """Generate untextured 3D geometry from image"""
    if geometry_pipeline is None:
        return None, "Error: Model not loaded"
    
    try:
        # Generate geometry
        generator = torch.Generator(device=geometry_pipeline.device).manual_seed(int(seed))
        out = geometry_pipeline(
            image,
            guidance_scale=guidance_scale,
            num_inference_steps=int(num_steps),
            generator=generator
        )
        
        # Export mesh
        output_path = f"/app/output/geometry_{seed}.glb"
        out.mesh[0].export(output_path)
        
        return output_path, f"✅ Generated untextured mesh (seed: {seed})"
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def generate_textured(image, guidance_scale, num_steps, seed):
    """Generate fully textured 3D model from image"""
    if geometry_pipeline is None or texture_pipeline is None:
        return None, "Error: Models not loaded"
    
    try:
        # Stage 1: Generate geometry
        generator = torch.Generator(device=geometry_pipeline.device).manual_seed(int(seed))
        out = geometry_pipeline(
            image,
            guidance_scale=guidance_scale,
            num_inference_steps=int(num_steps),
            generator=generator
        )
        
        # Get untextured mesh
        untextured_mesh = out.mesh[0]
        
        # Stage 2: Add texture
        untextured_mesh = remove_degenerate_face(untextured_mesh)
        untextured_mesh = reduce_face(untextured_mesh)
        textured_mesh = texture_pipeline(image, untextured_mesh)
        
        # Export
        output_path = f"/app/output/textured_{seed}.glb"
        textured_mesh.export(output_path)
        
        return output_path, f"✅ Generated textured mesh (seed: {seed})"
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# Load models on startup
print("🚀 Loading Step1X-3D models...")
load_models()
print("✅ Models ready!")

# Create Gradio interface with tabs
with gr.Blocks(title="Step1X-3D: Image to 3D") as demo:
    gr.Markdown("""
    # Step1X-3D: Image to 3D Generation
    
    Upload an image to generate high-quality 3D models.
    
    - **Geometry Only**: Fast, generates untextured mesh
    - **With Texture**: Slower, generates photorealistic textured model
    """)
    
    with gr.Tabs():
        # Tab 1: Geometry Only
        with gr.Tab("Geometry Only (Fast)"):
            with gr.Row():
                with gr.Column():
                    geom_image = gr.Image(type="filepath", label="Input Image")
                    geom_guidance = gr.Slider(1, 15, value=7.5, label="Guidance Scale")
                    geom_steps = gr.Slider(10, 100, value=50, step=10, label="Inference Steps")
                    geom_seed = gr.Number(value=2025, label="Random Seed")
                    geom_button = gr.Button("Generate Geometry", variant="primary")
                
                with gr.Column():
                    geom_output = gr.File(label="Download 3D Model (.glb)")
                    geom_status = gr.Textbox(label="Status", lines=2)
            
            geom_button.click(
                fn=generate_geometry,
                inputs=[geom_image, geom_guidance, geom_steps, geom_seed],
                outputs=[geom_output, geom_status]
            )
        
        # Tab 2: With Texture
        with gr.Tab("With Texture (Slow)"):
            with gr.Row():
                with gr.Column():
                    tex_image = gr.Image(type="filepath", label="Input Image")
                    tex_guidance = gr.Slider(1, 15, value=7.5, label="Guidance Scale")
                    tex_steps = gr.Slider(10, 100, value=50, step=10, label="Inference Steps")
                    tex_seed = gr.Number(value=2025, label="Random Seed")
                    tex_button = gr.Button("Generate Textured Model", variant="primary")
                
                with gr.Column():
                    tex_output = gr.File(label="Download 3D Model (.glb)")
                    tex_status = gr.Textbox(label="Status", lines=2)
            
            tex_button.click(
                fn=generate_textured,
                inputs=[tex_image, tex_guidance, tex_steps, tex_seed],
                outputs=[tex_output, tex_status]
            )
    
    gr.Markdown("""
    ---
    **Tips:**
    - Use clear, well-lit images for best results
    - Geometry-only generation is ~5x faster
    - Higher inference steps = better quality but slower
    - Guidance scale controls how closely it follows the image
    """)

# Launch
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

