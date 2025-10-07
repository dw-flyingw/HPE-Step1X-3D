"""
Simple Gradio client for HuggingFace Inference Endpoints
No local models, no dependencies, just API calls!
"""

import gradio as gr
import requests
from PIL import Image
import base64
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")

if not HF_TOKEN or not HF_ENDPOINT_URL:
    print("⚠️  Warning: HF_TOKEN or HF_ENDPOINT_URL not set in .env file")
    print("Please create a .env file with:")
    print("HF_TOKEN=your_token_here")
    print("HF_ENDPOINT_URL=your_endpoint_url_here")

def call_inference_endpoint(image, guidance_scale=7.5, num_steps=50, seed=2025):
    """
    Call HuggingFace Inference Endpoint
    """
    if not HF_TOKEN or not HF_ENDPOINT_URL:
        return None, "❌ Error: Please configure HF_TOKEN and HF_ENDPOINT_URL in .env file"
    
    try:
        # Convert image to base64
        if isinstance(image, str):
            img = Image.open(image)
        else:
            img = image
        
        # Resize if too large (optional, saves bandwidth)
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": img_str,
            "parameters": {
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_steps,
                "seed": seed
            }
        }
        
        # Call endpoint
        status_msg = "🚀 Sending request to HuggingFace..."
        print(status_msg)
        
        response = requests.post(
            HF_ENDPOINT_URL,
            headers=headers,
            json=payload,
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code == 200:
            # Save the returned 3D model
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"model_{seed}.glb")
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return output_path, f"✅ Generated successfully! (seed: {seed})"
        
        elif response.status_code == 503:
            return None, "⏳ Endpoint is starting up (scaled from zero). Please wait 30-60 seconds and try again."
        
        elif response.status_code == 401:
            return None, "❌ Unauthorized: Check your HF_TOKEN in .env file"
        
        else:
            error_msg = f"❌ Error {response.status_code}: {response.text}"
            print(error_msg)
            return None, error_msg
    
    except requests.exceptions.Timeout:
        return None, "❌ Timeout: Generation took too long. Try reducing inference steps."
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return None, error_msg

# Create Gradio interface
with gr.Blocks(title="Step1X-3D via HuggingFace") as demo:
    gr.Markdown("""
    # 🚀 Step1X-3D via HuggingFace Inference Endpoints
    
    Upload an image to generate a 3D model using HuggingFace's managed infrastructure.
    
    **No local models needed!** Everything runs on HuggingFace servers.
    """)
    
    # Configuration status
    config_status = gr.Markdown()
    
    if HF_TOKEN and HF_ENDPOINT_URL:
        config_status.value = """
        ✅ **Configuration OK**
        - HF_TOKEN: Set
        - HF_ENDPOINT_URL: Set
        """
    else:
        config_status.value = """
        ⚠️ **Configuration Missing**
        
        Please create a `.env` file with:
        ```
        HF_TOKEN=your_token_here
        HF_ENDPOINT_URL=your_endpoint_url_here
        ```
        
        See `HF_INFERENCE_ENDPOINTS_GUIDE.md` for setup instructions.
        """
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Input Image")
            
            with gr.Accordion("Advanced Settings", open=False):
                guidance_scale = gr.Slider(
                    minimum=1.0,
                    maximum=15.0,
                    value=7.5,
                    step=0.5,
                    label="Guidance Scale"
                )
                num_steps = gr.Slider(
                    minimum=10,
                    maximum=100,
                    value=50,
                    step=10,
                    label="Inference Steps"
                )
                seed = gr.Number(value=2025, label="Random Seed")
            
            generate_btn = gr.Button("🎨 Generate 3D Model", variant="primary", size="lg")
        
        with gr.Column():
            output_file = gr.File(label="📥 Download 3D Model (.glb)")
            status_output = gr.Textbox(label="Status", lines=5)
    
    generate_btn.click(
        fn=call_inference_endpoint,
        inputs=[image_input, guidance_scale, num_steps, seed],
        outputs=[output_file, status_output]
    )
    
    gr.Markdown("""
    ---
    ### 💡 Tips
    - First request may take 30-60 seconds (endpoint starting up)
    - Subsequent requests are faster
    - Use clear, well-lit images for best results
    - Generation takes about 30-60 seconds
    
    ### 💰 Cost
    - ~$0.60/hour when running
    - $0/hour when idle (if min replicas = 0)
    - Check your HuggingFace dashboard for usage
    
    ### 📚 Resources
    - Setup Guide: `HF_INFERENCE_ENDPOINTS_GUIDE.md`
    - HF Dashboard: https://ui.endpoints.huggingface.co/
    - Model Page: https://huggingface.co/stepfun-ai/Step1X-3D
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

