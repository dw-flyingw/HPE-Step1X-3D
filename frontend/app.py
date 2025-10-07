"""
Step1X-3D Frontend - Streamlit Application
Modern UI for 3D model generation and processing
"""

import streamlit as st
import requests
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Configure page
st.set_page_config(
    page_title="Step1X-3D Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", 8501))

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #4CAF50;
        box-shadow: 0 0 10px #4CAF50;
    }
    
    .status-offline {
        background-color: #f44336;
        box-shadow: 0 0 10px #f44336;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .generation-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #fafafa;
    }
    
    .success-card {
        border-color: #4CAF50;
        background: #f1f8e9;
    }
    
    .error-card {
        border-color: #f44336;
        background: #ffebee;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "backend_status" not in st.session_state:
    st.session_state.backend_status = {"online": False, "last_check": 0}
if "generated_files" not in st.session_state:
    st.session_state.generated_files = []


def check_backend_status() -> Dict[str, Any]:
    """Check backend status and return information"""
    try:
        response = requests.get(f"{BACKEND_URL}/health/", timeout=5)
        if response.status_code == 200:
            return {
                "online": True,
                "data": response.json(),
                "last_check": time.time()
            }
        else:
            return {
                "online": False,
                "error": f"HTTP {response.status_code}",
                "last_check": time.time()
            }
    except Exception as e:
        return {
            "online": False,
            "error": str(e),
            "last_check": time.time()
        }


def display_backend_status():
    """Display backend status in sidebar"""
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        
        # Check backend status (cache for 30 seconds)
        current_time = time.time()
        if current_time - st.session_state.backend_status.get("last_check", 0) > 30:
            st.session_state.backend_status = check_backend_status()
        
        status = st.session_state.backend_status
        
        if status["online"]:
            st.markdown(
                f'<div class="status-indicator status-online"></div>'
                f'<strong>Backend Online</strong>',
                unsafe_allow_html=True
            )
            
            # Display system info
            data = status["data"]
            
            # GPU Info
            gpu_info = data.get("gpu_info", {})
            if gpu_info.get("available"):
                st.metric("GPU Count", gpu_info["count"])
                
                for i, device in enumerate(gpu_info.get("devices", [])[:2]):  # Show first 2 GPUs
                    memory_used = device.get("memory_allocated", 0) / (1024**3)  # GB
                    memory_total = device.get("memory_total", 0) / (1024**3)  # GB
                    st.metric(f"GPU {i} Memory", f"{memory_used:.1f}/{memory_total:.1f} GB")
            
            # Model Status
            models = data.get("models", {})
            for model_name, model_info in models.items():
                status_icon = "✅" if model_info.get("loaded") else "❌"
                st.write(f"{status_icon} {model_name.title()}")
                
        else:
            st.markdown(
                f'<div class="status-indicator status-offline"></div>'
                f'<strong>Backend Offline</strong>',
                unsafe_allow_html=True
            )
            if "error" in status:
                st.error(f"Error: {status['error']}")


def generate_text_to_image(prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Generate image from text prompt"""
    try:
        with st.spinner("Generating image from prompt..."):
            response = requests.post(
                f"{BACKEND_URL}/api/v1/text-to-image",
                data={
                    "prompt": prompt,
                    "width": kwargs.get("width", 1024),
                    "height": kwargs.get("height", 1024),
                    "num_inference_steps": kwargs.get("num_inference_steps", 20),
                    "guidance_scale": kwargs.get("guidance_scale", 7.5),
                    "seed": kwargs.get("seed")
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                st.error(f"Image generation failed: {response.text}")
                return None
                
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None


def generate_3d_model(image_bytes: bytes, filename: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Generate 3D model from image"""
    try:
        with st.spinner(f"Generating {kwargs.get('mode', 'geometry')} 3D model... This may take 30-60 seconds"):
            files = {"image": (filename, image_bytes, "image/png")}
            data = {
                "mode": kwargs.get("mode", "geometry"),
                "guidance_scale": kwargs.get("guidance_scale", 7.5),
                "num_steps": kwargs.get("num_steps", 50),
                "seed": kwargs.get("seed", 2025)
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/generate-3d",
                files=files,
                data=data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                st.error(f"3D generation failed: {response.text}")
                return None
                
    except Exception as e:
        st.error(f"Error generating 3D model: {str(e)}")
        return None


def convert_mesh(file_bytes: bytes, filename: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Convert mesh file"""
    try:
        with st.spinner("Converting mesh..."):
            files = {"file": (filename, file_bytes)}
            data = {
                "prompt": kwargs.get("prompt"),
                "target_format": kwargs.get("target_format", "glb"),
                "quality": kwargs.get("quality", "high")
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/convert-mesh",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                st.error(f"Mesh conversion failed: {response.text}")
                return None
                
    except Exception as e:
        st.error(f"Error converting mesh: {str(e)}")
        return None


def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Step1X-3D Generator</h1>
        <p>Transform images and text into stunning 3D models using AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with system status and settings
    display_backend_status()
    
    # Generation settings
    with st.sidebar:
        st.markdown("### ⚙️ Generation Settings")
        
        mode = st.radio(
            "Generation Mode",
            ["geometry", "textured"],
            format_func=lambda x: "Geometry Only (Fast)" if x == "geometry" else "With Texture (Detailed)",
            help="Geometry is faster but untextured. Textured includes colors and materials."
        )
        
        guidance_scale = st.slider(
            "Guidance Scale",
            min_value=1.0,
            max_value=15.0,
            value=7.5,
            step=0.5,
            help="Higher values follow the image more closely"
        )
        
        num_steps = st.slider(
            "Inference Steps",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="More steps = better quality but slower"
        )
        
        seed = st.number_input(
            "Random Seed",
            min_value=0,
            max_value=999999,
            value=2025,
            step=1,
            help="Same seed produces same result"
        )
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Generate from Image",
        "✍️ Generate from Prompt", 
        "🔄 Modify 3D Model",
        "📂 View 3D Models",
        "📊 System Monitor"
    ])
    
    # Tab 1: Generate from Image
    with tab1:
        st.subheader("📤 Upload Image to Generate 3D Model")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=["png", "jpg", "jpeg"],
                help="Upload a clear image of an object to convert to 3D"
            )
            
            if uploaded_file:
                from PIL import Image
                image = Image.open(uploaded_file)
                st.image(image, caption="Input Image", use_column_width=True)
                st.caption(f"Size: {image.size[0]}x{image.size[1]} | Format: {uploaded_file.type}")
        
        with col2:
            st.subheader("📥 Generated 3D Model")
            
            if uploaded_file:
                if st.button("🚀 Generate 3D Model", type="primary", use_container_width=True):
                    result = generate_3d_model(
                        image_bytes=uploaded_file.getvalue(),
                        filename=uploaded_file.name,
                        mode=mode,
                        guidance_scale=guidance_scale,
                        num_steps=num_steps,
                        seed=seed
                    )
                    
                    if result:
                        st.success("✅ Generation complete!")
                        
                        # Download button
                        download_url = f"{BACKEND_URL}/api/v1/download/{result['filename']}"
                        st.download_button(
                            label="📥 Download 3D Model",
                            data=requests.get(download_url).content,
                            file_name=result['filename'],
                            mime="model/gltf-binary",
                            use_container_width=True
                        )
                        
                        # Show metadata
                        with st.expander("Generation Details"):
                            st.json(result['metadata'])
            else:
                st.info("👈 Upload an image to get started")
    
    # Tab 2: Generate from Prompt
    with tab2:
        st.subheader("✍️ Generate 3D Model from Text Prompt")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            prompt = st.text_area(
                "Describe what you want to create",
                placeholder="e.g., a red sports car, a wooden chair, a futuristic robot...",
                height=100
            )
            
            if st.button("🎨 Generate Image from Prompt", use_container_width=True):
                if prompt:
                    result = generate_text_to_image(prompt)
                    if result:
                        st.session_state['generated_image'] = result
                        st.success("✅ Image generated!")
                else:
                    st.warning("Please enter a prompt")
        
        with col2:
            st.subheader("📥 Generated 3D Model")
            
            if 'generated_image' in st.session_state:
                result = st.session_state['generated_image']
                st.success("✅ Image ready! Generate 3D →")
                
                if st.button("🚀 Generate 3D from This Image", use_container_width=True):
                    # Download the generated image
                    img_response = requests.get(f"{BACKEND_URL}/api/v1/download/{result['filename']}")
                    
                    # Generate 3D model
                    model_result = generate_3d_model(
                        image_bytes=img_response.content,
                        filename=result['filename'],
                        mode=mode,
                        guidance_scale=guidance_scale,
                        num_steps=num_steps,
                        seed=seed
                    )
                    
                    if model_result:
                        st.success("✅ 3D model generated!")
                        
                        # Download button
                        download_url = f"{BACKEND_URL}/api/v1/download/{model_result['filename']}"
                        st.download_button(
                            label="📥 Download 3D Model",
                            data=requests.get(download_url).content,
                            file_name=model_result['filename'],
                            mime="model/gltf-binary",
                            use_container_width=True
                        )
            else:
                st.info("👈 Generate an image first")
    
    # Tab 3: Modify 3D Model
    with tab3:
        st.subheader("🔄 Modify Existing 3D Model")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            existing_model = st.file_uploader(
                "Upload 3D Model",
                type=["glb", "obj", "nii.gz"],
                help="Upload .glb, .obj, or .nii.gz file"
            )
            
            modification_prompt = st.text_area(
                "What modifications do you want to apply?",
                placeholder="e.g., add red texture, make it smoother, add details...",
                height=100
            )
            
            target_format = st.selectbox(
                "Target Format",
                ["glb", "obj", "stl", "ply"],
                help="Choose the output format"
            )
        
        with col2:
            st.subheader("📥 Modified Model")
            
            if existing_model:
                if st.button("🔄 Convert/Modify Model", use_container_width=True):
                    result = convert_mesh(
                        file_bytes=existing_model.getvalue(),
                        filename=existing_model.name,
                        prompt=modification_prompt,
                        target_format=target_format,
                        quality="high"
                    )
                    
                    if result:
                        st.success("✅ Conversion complete!")
                        
                        # Download button
                        download_url = f"{BACKEND_URL}/api/v1/download/{result['filename']}"
                        st.download_button(
                            label="📥 Download Modified Model",
                            data=requests.get(download_url).content,
                            file_name=result['filename'],
                            mime="application/octet-stream",
                            use_container_width=True
                        )
                        
                        # Show mesh info
                        with st.expander("Mesh Information"):
                            st.json(result['mesh_info'])
            else:
                st.info("👈 Upload a 3D model file")
    
    # Tab 4: View 3D Models
    with tab4:
        st.subheader("📂 View and Manage Generated Models")
        
        # List generated files
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/files")
            if response.status_code == 200:
                files_data = response.json()
                
                if files_data['files']:
                    st.write(f"**Found {files_data['total']} generated files:**")
                    
                    for file_info in files_data['files'][:10]:  # Show first 10
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.write(f"📄 {file_info['filename']}")
                        
                        with col2:
                            st.write(f"Size: {file_info['size'] / 1024:.1f} KB")
                        
                        with col3:
                            st.write(f"Created: {time.strftime('%Y-%m-%d %H:%M', time.localtime(file_info['created']))}")
                        
                        with col4:
                            if st.button("📥", key=f"download_{file_info['filename']}", help="Download"):
                                download_url = f"{BACKEND_URL}/api/v1/download/{file_info['filename']}"
                                st.download_button(
                                    "Download",
                                    requests.get(download_url).content,
                                    file_info['filename'],
                                    key=f"dl_{file_info['filename']}"
                                )
                else:
                    st.info("No generated files found")
            else:
                st.error("Failed to load file list")
                
        except Exception as e:
            st.error(f"Error loading files: {str(e)}")
    
    # Tab 5: System Monitor
    with tab5:
        st.subheader("📊 System Monitoring")
        
        # Get detailed system info
        try:
            response = requests.get(f"{BACKEND_URL}/health/")
            if response.status_code == 200:
                data = response.json()
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 🖥️ System Information")
                    system_info = data.get('system_info', {})
                    st.metric("CPU Cores", system_info.get('cpu_count', 'N/A'))
                    st.metric("Memory Used", f"{system_info.get('memory_used_percent', 0):.1f}%")
                    st.metric("Python Version", system_info.get('python_version', 'N/A'))
                
                with col2:
                    st.markdown("### 🎮 GPU Information")
                    gpu_info = data.get('gpu_info', {})
                    if gpu_info.get('available'):
                        st.metric("GPU Count", gpu_info['count'])
                        
                        for i, device in enumerate(gpu_info.get('devices', [])):
                            with st.expander(f"GPU {i}: {device.get('name', 'Unknown')}"):
                                st.metric("Total Memory", f"{device.get('memory_total', 0) / (1024**3):.1f} GB")
                                st.metric("Used Memory", f"{device.get('memory_allocated', 0) / (1024**3):.1f} GB")
                                st.metric("Free Memory", f"{device.get('memory_free', 0) / (1024**3):.1f} GB")
                    else:
                        st.warning("No GPU available")
                
                # Model Status
                st.markdown("### 🤖 Model Status")
                models = data.get('models', {})
                for model_name, model_info in models.items():
                    status = "✅ Loaded" if model_info.get('loaded') else "❌ Not Loaded"
                    st.write(f"**{model_name.title()}**: {status}")
                    
                    if model_info.get('loaded'):
                        with st.expander(f"{model_name.title()} Details"):
                            st.json(model_info)
                            
            else:
                st.error("Failed to get system information")
                
        except Exception as e:
            st.error(f"Error getting system info: {str(e)}")


if __name__ == "__main__":
    main()
