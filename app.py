import os, uuid, torch, streamlit as st, trimesh, tempfile
from step1x3d_geometry.models.pipelines.pipeline import Step1X3DGeometryPipeline
from step1x3d_texture.pipelines.step1x_3d_texture_synthesis_pipeline import Step1X3DTexturePipeline

st.set_page_config(page_title="Step1X-3D ‑ uv + streamlit", layout="centered")

@st.cache_resource(show_spinner=False)
def load_pipes():
    geom = Step1X3DGeometryPipeline.from_pretrained("stepfun-ai/Step1X-3D-Geometry")
    tex  = Step1X3DTexturePipeline.from_pretrained("stepfun-ai/Step1X-3D-Texture")
    return geom, tex

geom_pipe, tex_pipe = load_pipes()

st.title("Step1X-3D – text ➜ 3-D mesh")
prompt = st.text_input("Prompt", "a cute robot made of wood")
seed   = st.number_input("Seed", value=42, step=1)
do_tex = st.checkbox("Generate texture", value=True)

if st.button("Generate", type="primary"):
    with st.spinner("Running geometry pipeline …"):
        mesh_path = geom_pipe(prompt=prompt, seed=seed, output_type="glb")
    st.success("Geometry done")
    if do_tex:
        with st.spinner("Running texture pipeline …"):
            mesh_path = tex_pipe(mesh_path, prompt=prompt)
        st.success("Texture done")

    # show in browser
    with open(mesh_path, "rb") as f:
        st.download_button("Download GLB", f, file_name=os.path.basename(mesh_path))
    st.markdown("---")
    st.markdown(
        f'<model-viewer src="data:model/gltf-binary;base64,{f.read().encode("base64").decode()}" '
        'style="height:400px;width:100%" camera-controls></model-viewer>',
        unsafe_allow_html=True,
    )
