"""
Streamlit Frontend for Step1X-3D
"""

import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Step1X-3D Generator",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Step1X-3D: Image to 3D Model")
st.markdown("Upload an image to generate a 3D model using AI")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Generation Settings")
    
    mode = st.radio(
        "Generation Mode",
        ["geometry", "textured"],
        format_func=lambda x: "Geometry Only (Fast)" if x == "geometry" else "With Texture (Detailed)",
        help="Geometry is faster but untextured. Textured includes colors and materials."
    )
    
    st.markdown("---")
    
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
    
    st.markdown("---")
    
    # Backend status
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Backend Online")
            if not data.get("hf_token_set"):
                st.warning("⚠️ HF_TOKEN not configured in backend")
        else:
            st.error(f"❌ Backend returned {response.status_code}")
    except Exception as e:
        st.error(f"❌ Backend Offline: {str(e)}")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Input Image")
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"],
        help="Upload a clear image of an object to convert to 3D"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Input Image", use_column_width=True)
        
        # Show image info
        st.caption(f"Size: {image.size[0]}x{image.size[1]} | Format: {image.format}")

with col2:
    st.subheader("📥 Generated 3D Model")
    
    if uploaded_file:
        if st.button("🚀 Generate 3D Model", type="primary", use_container_width=True):
            
            with st.spinner(f"Generating {mode} model... This may take 30-60 seconds"):
                try:
                    # Prepare request
                    files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "mode": mode,
                        "guidance_scale": guidance_scale,
                        "num_steps": num_steps,
                        "seed": seed
                    }
                    
                    # Call backend
                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        files=files,
                        data=data,
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        # Save and display download
                        output_filename = f"{mode}_{seed}.glb"
                        
                        st.success("✅ Generation complete!")
                        st.download_button(
                            label="📥 Download 3D Model (.glb)",
                            data=response.content,
                            file_name=output_filename,
                            mime="model/gltf-binary",
                            use_container_width=True
                        )
                        
                        # Show file info
                        file_size = len(response.content) / 1024  # KB
                        st.caption(f"File: {output_filename} | Size: {file_size:.1f} KB")
                    
                    elif response.status_code == 503:
                        st.warning("⏳ Model is loading. Please wait 30-60 seconds and try again.")
                    
                    elif response.status_code == 401:
                        st.error("❌ Invalid HF token. Check backend configuration.")
                    
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"❌ Error: {error_detail}")
                
                except requests.exceptions.Timeout:
                    st.error("❌ Request timeout. Try reducing inference steps.")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure it's running on port 8000.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("👈 Upload an image to get started")

# Footer
st.markdown("---")

with st.expander("💡 Tips & Information"):
    st.markdown("""
    ### How to Use
    1. Upload a clear image of an object
    2. Choose generation mode (geometry or textured)
    3. Adjust settings if needed
    4. Click "Generate 3D Model"
    5. Download the .glb file
    
    ### Generation Modes
    - **Geometry Only**: Fast (~30-60 sec), untextured mesh
    - **With Texture**: Slower (~2-5 min), photorealistic with colors
    
    ### Tips for Best Results
    - Use clear, well-lit images
    - Single object with plain background works best
    - Higher inference steps = better quality but slower
    - Try different seeds for variations
    
    ### File Format
    The generated .glb files can be viewed in:
    - Blender (free 3D software)
    - Online viewers (e.g., gltf-viewer.donmccurdy.com)
    - Three.js applications
    - Unity/Unreal Engine
    """)

st.markdown("""
<style>
    .stButton>button {
        height: 3em;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

