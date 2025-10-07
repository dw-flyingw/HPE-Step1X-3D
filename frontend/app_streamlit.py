"""
Simple Streamlit frontend for Step1X-3D
Works with the Gradio backend via API
"""

import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(
    page_title="Step1X-3D Generator",
    page_icon="🎨",
    layout="wide"
)

# Configuration
GRADIO_URL = "http://localhost:7860"  # Change if running on different port/host

st.title("🎨 Step1X-3D: Image to 3D Generator")
st.markdown("Upload an image to generate a 3D model")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_type = st.radio(
        "Model Type",
        ["Geometry Only (Fast)", "With Texture (Detailed)"],
        help="Geometry only is faster but without colors"
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
        help="Use same seed for reproducible results"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Status")
    status_text = st.empty()
    status_text.info("Ready to generate")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.header("📤 Input")
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"],
        help="Upload a clear image of an object"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Input Image", use_column_width=True)

with col2:
    st.header("📥 Output")
    
    if uploaded_file:
        if st.button("🚀 Generate 3D Model", type="primary", use_container_width=True):
            with st.spinner("Generating 3D model... This may take 1-5 minutes"):
                try:
                    status_text.warning("Sending request to backend...")
                    
                    # Determine endpoint
                    if "Geometry Only" in model_type:
                        endpoint = f"{GRADIO_URL}/api/predict"
                        api_name = "generate_geometry"
                    else:
                        endpoint = f"{GRADIO_URL}/api/predict"
                        api_name = "generate_textured"
                    
                    # Prepare request
                    files = {"data": uploaded_file.getvalue()}
                    data = {
                        "data": [
                            uploaded_file.name,  # image
                            guidance_scale,
                            num_steps,
                            seed
                        ]
                    }
                    
                    status_text.warning("Processing on GPU... Please wait")
                    
                    # Make request (simplified - you may need gradio_client for full API)
                    # For now, show instructions
                    st.info("""
                    **To complete the integration:**
                    
                    1. Install gradio_client:
                       ```
                       pip install gradio-client
                       ```
                    
                    2. Or access the Gradio UI directly at:
                       http://localhost:7860
                    
                    3. Upload your image there and download the result
                    """)
                    
                    # Example code for when using gradio_client:
                    st.code("""
from gradio_client import Client

client = Client("http://localhost:7860")
result = client.predict(
    image="path/to/image.png",
    guidance_scale=7.5,
    num_steps=50,
    seed=2025,
    api_name="/generate_geometry"  # or "/generate_textured"
)
                    """, language="python")
                    
                    status_text.success("Open Gradio UI to complete generation")
                    
                except Exception as e:
                    status_text.error(f"Error: {str(e)}")
                    st.error(f"Failed to generate: {str(e)}")
    else:
        st.info("👈 Upload an image to get started")

# Footer
st.markdown("---")
st.markdown("""
### 💡 Tips
- Use clear, well-lit images for best results
- Geometry-only generation is 5x faster than textured
- Higher inference steps improve quality but take longer
- Try different seeds for variations

### 🔗 Direct Access
Access the Gradio interface directly at: [http://localhost:7860](http://localhost:7860)
""")

