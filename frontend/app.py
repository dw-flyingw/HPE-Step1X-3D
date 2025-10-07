"""
Streamlit Frontend for Step1X-3D
"""

import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv
import trimesh
import tempfile
import base64
import nibabel as nib
import numpy as np

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

# Add tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Generate from Image", 
    "✍️ Generate from Prompt",
    "🔄 Modify 3D Model",
    "📂 View 3D Model"
])

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

# Tab 1: Generate 3D
with tab1:
    st.subheader("📤 Input")
    
    # Option to use prompt or upload
    input_method = st.radio(
        "Choose input method:",
        ["Upload Image", "Generate from Text Prompt"],
        horizontal=True
    )
    
    col1, col2 = st.columns([1, 1])

    with col1:
        if input_method == "Upload Image":
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg"],
                help="Upload a clear image of an object to convert to 3D"
            )
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Input Image", use_column_width=True)
                st.caption(f"Size: {image.size[0]}x{image.size[1]} | Format: {image.format}")
        
        else:  # Generate from prompt
            prompt_input = st.text_area(
                "Describe what you want to create",
                placeholder="e.g., a red sports car, a wooden chair, a futuristic robot...",
                height=150,
                key="tab1_prompt"
            )
            
            if prompt_input and st.button("🎨 Generate Image", use_container_width=True, key="tab1_gen_img"):
                with st.spinner("Generating image from prompt..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/text-to-image",
                            data={"prompt": prompt_input},
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            generated_img = Image.open(io.BytesIO(response.content))
                            st.image(generated_img, caption="Generated Image", use_column_width=True)
                            st.session_state['tab1_generated_image'] = response.content
                            st.success("✅ Image ready! Generate 3D →")
                        else:
                            st.error(f"❌ Failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            # Show generated image if exists
            if 'tab1_generated_image' in st.session_state:
                st.image(
                    Image.open(io.BytesIO(st.session_state['tab1_generated_image'])), 
                    caption="Generated Image",
                    use_column_width=True
                )
    
    with col2:
        st.subheader("📥 Generated 3D Model")
        
        # Determine which image to use
        has_image = False
        image_source = None
        
        if input_method == "Upload Image" and uploaded_file:
            has_image = True
            image_source = ("uploaded", uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        elif input_method == "Generate from Text Prompt" and 'tab1_generated_image' in st.session_state:
            has_image = True
            image_source = ("generated", "generated.png", st.session_state['tab1_generated_image'], "image/png")
        
        if has_image:
            if st.button("🚀 Generate 3D Model", type="primary", use_container_width=True, key="tab1_gen_3d"):
                
                with st.spinner(f"Generating {mode} model... This may take 30-60 seconds"):
                    try:
                        # Prepare request with the appropriate image source
                        _, filename, content, content_type = image_source
                        files = {"image": (filename, content, content_type)}
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
            if input_method == "Upload Image":
                st.info("👈 Upload an image to get started")
            else:
                st.info("👈 Enter a text prompt to generate an image first")

# Tab 2: Generate from Text Prompt
with tab2:
    st.subheader("✍️ Generate 3D from Text Prompt")
    st.markdown("Enter a text description to generate an image, then create a 3D model")
    
    text_prompt = st.text_area(
        "Describe what you want to create",
        placeholder="e.g., a red sports car, a wooden chair, a futuristic robot...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if text_prompt and st.button("🎨 Generate Image from Prompt", use_container_width=True):
            with st.spinner("Generating image from prompt..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/text-to-image",
                        data={"prompt": text_prompt},
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        generated_img = Image.open(io.BytesIO(response.content))
                        st.image(generated_img, caption="Generated Image", use_column_width=True)
                        
                        # Store in session state for 3D generation
                        st.session_state['generated_image'] = response.content
                        st.success("✅ Image generated! Now generate 3D model →")
                    else:
                        st.error(f"❌ Image generation failed: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if 'generated_image' in st.session_state:
            st.markdown("**Generated Image Preview**")
            st.image(Image.open(io.BytesIO(st.session_state['generated_image'])), use_column_width=True)
            
            if st.button("🚀 Generate 3D from This Image", use_container_width=True):
                with st.spinner(f"Generating {mode} 3D model..."):
                    try:
                        files = {"image": ("generated.png", st.session_state['generated_image'], "image/png")}
                        data = {
                            "mode": mode,
                            "guidance_scale": guidance_scale,
                            "num_steps": num_steps,
                            "seed": seed
                        }
                        
                        response = requests.post(
                            f"{BACKEND_URL}/generate",
                            files=files,
                            data=data,
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            output_filename = f"prompt_{seed}.glb"
                            st.success("✅ 3D model generated!")
                            st.download_button(
                                label="📥 Download 3D Model (.glb)",
                                data=response.content,
                                file_name=output_filename,
                                mime="model/gltf-binary",
                                use_container_width=True
                            )
                        else:
                            st.error(f"❌ 3D generation failed")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👈 Generate an image first")

# Tab 3: Modify Existing 3D Model
with tab3:
    st.subheader("🔄 Modify Existing 3D Model")
    st.markdown("Upload a 3D model and apply modifications based on a text prompt")
    
    col1, col2 = st.columns(2)
    
    with col1:
        existing_model = st.file_uploader(
            "Upload 3D Model",
            type=["glb", "obj", "nii.gz"],
            key="modify_upload",
            help="Upload .glb, .obj, or .nii.gz file"
        )
        
        if existing_model:
            file_ext = existing_model.name.split('.')[-1]
            st.caption(f"Uploaded: {existing_model.name} ({file_ext.upper()})")
            
            modification_prompt = st.text_area(
                "What modifications do you want to apply?",
                placeholder="e.g., add red texture, make it smoother, add details...",
                height=100
            )
    
    with col2:
        if existing_model:
            # Show model info
            st.markdown("**Model Information**")
            
            try:
                # Convert to mesh for preview
                response = requests.post(
                    f"{BACKEND_URL}/convert-to-mesh",
                    files={"file": (existing_model.name, existing_model.getvalue())},
                    data={"prompt": modification_prompt} if modification_prompt else {},
                    timeout=60
                )
                
                if response.status_code == 200:
                    st.success("✅ Model loaded successfully")
                    
                    if modification_prompt:
                        st.download_button(
                            label="📥 Download Modified Model",
                            data=response.content,
                            file_name=f"modified_{existing_model.name.split('.')[0]}.glb",
                            mime="model/gltf-binary",
                            use_container_width=True
                        )
                    else:
                        st.info("Enter a modification prompt to process the model")
                        st.download_button(
                            label="📥 Download Converted Model (.glb)",
                            data=response.content,
                            file_name=f"converted_{existing_model.name.split('.')[0]}.glb",
                            mime="model/gltf-binary",
                            use_container_width=True
                        )
                else:
                    st.error(f"❌ Conversion failed: {response.text}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👈 Upload a 3D model file")

# Tab 4: View 3D Models
with tab4:
    st.subheader("📂 Load and View 3D Models")
    st.markdown("Upload a .glb or .obj file to view its properties")
    
    model_file = st.file_uploader(
        "Upload 3D Model",
        type=["glb", "obj", "nii.gz"],
        key="view_upload",
        help="Upload a .glb, .obj, or .nii.gz file"
    )
    
    if model_file:
        try:
            file_ext = model_file.name.split('.')[-1].lower()
            
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
                tmp.write(model_file.getvalue())
                tmp_path = tmp.name
            
            # Load based on file type
            if file_ext in ['glb', 'obj']:
                mesh = trimesh.load(tmp_path)
            
            elif file_ext == 'gz' and model_file.name.endswith('.nii.gz'):
                # Load NIfTI file
                nii_img = nib.load(tmp_path)
                data = nii_img.get_fdata()
                
                # Create mesh from volume using marching cubes
                from skimage import measure
                threshold = data.mean() + data.std()
                verts, faces, normals, values = measure.marching_cubes(data, threshold)
                mesh = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals)
            
            else:
                st.error(f"Unsupported file type: {file_ext}")
                mesh = None
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            if mesh is None:
                st.stop()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Model Information")
                
                if hasattr(mesh, 'vertices'):
                    st.metric("Vertices", f"{len(mesh.vertices):,}")
                    st.metric("Faces", f"{len(mesh.faces):,}")
                    
                    if hasattr(mesh, 'bounds'):
                        bounds = mesh.bounds
                        size = bounds[1] - bounds[0]
                        st.metric("Bounding Box", f"{size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f}")
                    
                    if hasattr(mesh, 'is_watertight'):
                        st.metric("Watertight", "✅ Yes" if mesh.is_watertight else "❌ No")
                    
                    if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'material'):
                        st.metric("Has Material", "✅ Yes")
                    else:
                        st.metric("Has Material", "❌ No")
                
                # File info
                file_size = len(model_file.getvalue()) / 1024  # KB
                st.caption(f"File size: {file_size:.1f} KB")
            
            with col2:
                st.markdown("### 🔄 Export Options")
                
                st.markdown("**Available formats:**")
                
                # Convert and download buttons
                if st.button("📥 Download as .glb", use_container_width=True):
                    output = io.BytesIO()
                    mesh.export(output, file_type='glb')
                    st.download_button(
                        label="💾 Save .glb",
                        data=output.getvalue(),
                        file_name=f"{model_file.name.split('.')[0]}.glb",
                        mime="model/gltf-binary"
                    )
                
                if st.button("📥 Download as .obj", use_container_width=True):
                    output = io.BytesIO()
                    mesh.export(output, file_type='obj')
                    st.download_button(
                        label="💾 Save .obj",
                        data=output.getvalue(),
                        file_name=f"{model_file.name.split('.')[0]}.obj",
                        mime="model/obj"
                    )
                
                if st.button("📥 Download as .stl", use_container_width=True):
                    output = io.BytesIO()
                    mesh.export(output, file_type='stl')
                    st.download_button(
                        label="💾 Save .stl",
                        data=output.getvalue(),
                        file_name=f"{model_file.name.split('.')[0]}.stl",
                        mime="model/stl"
                    )
                
                # Add .ply export option
                if st.button("📥 Download as .ply", use_container_width=True):
                    output = io.BytesIO()
                    mesh.export(output, file_type='ply')
                    st.download_button(
                        label="💾 Save .ply",
                        data=output.getvalue(),
                        file_name=f"{model_file.name.split('.')[0]}.ply",
                        mime="application/octet-stream"
                    )
            
            # Show mesh preview info
            st.markdown("---")
            with st.expander("📐 Detailed Mesh Information"):
                mesh_info = {
                    "file_name": model_file.name,
                    "file_type": model_file.name.split('.')[-1].upper(),
                    "vertices": len(mesh.vertices) if hasattr(mesh, 'vertices') else "N/A",
                    "faces": len(mesh.faces) if hasattr(mesh, 'faces') else "N/A",
                    "is_watertight": str(mesh.is_watertight) if hasattr(mesh, 'is_watertight') else "N/A",
                    "has_normals": hasattr(mesh, 'vertex_normals'),
                    "has_colors": hasattr(mesh.visual, 'vertex_colors') if hasattr(mesh, 'visual') else False,
                }
                
                # Add NIfTI-specific info
                if model_file.name.endswith('.nii.gz'):
                    mesh_info["original_format"] = "NIfTI (Medical Imaging)"
                    mesh_info["converted_to_mesh"] = "Using Marching Cubes"
                
                st.json(mesh_info)
        
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    else:
        st.info("👈 Upload a .glb, .obj, or .nii.gz file to view its properties")

# Footer
st.markdown("---")

with st.expander("💡 Tips & Information"):
    st.markdown("""
    ### 🚀 Generate from Image Tab
    - Upload an image to create a 3D model
    - Choose geometry (fast) or textured (detailed)
    
    ### ✍️ Generate from Prompt Tab
    - Enter text description → generates image → creates 3D model
    - Two-step process: text → image → 3D
    
    ### 🔄 Modify 3D Model Tab
    - Upload existing .glb, .obj, or .nii.gz file
    - Convert between different 3D formats
    - Apply modifications (if prompt provided)
    
    ### 📂 View 3D Model Tab
    - View mesh statistics (vertices, faces, watertight, etc.)
    - Convert between formats (.glb ↔ .obj ↔ .stl ↔ .ply)
    - Download in different formats
    
    ### Generation Modes
    - **Geometry Only**: Fast (~30-60 sec), untextured mesh
    - **With Texture**: Slower (~2-5 min), photorealistic with colors
    
    ### Tips for Best Results
    - Use clear, well-lit images
    - Single object with plain background works best
    - Higher inference steps = better quality but slower
    - Try different seeds for variations
    
    ### Supported 3D Formats
    - **Load**: .glb, .obj, .nii.gz (medical imaging)
    - **Export**: .glb, .obj, .stl, .ply
    - **Viewers**: Blender, MeshLab, online viewers, Unity, Unreal Engine
    
    ### NIfTI (.nii.gz) Support
    - Medical imaging format commonly used in healthcare
    - Automatically converts volume data to mesh using marching cubes
    - Useful for medical visualization
    """)

st.markdown("""
<style>
    .stButton>button {
        height: 3em;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

