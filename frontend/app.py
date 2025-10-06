
import streamlit as st
import requests
import os

st.title("Step1X-3D Model Generator")

prompt = st.text_input("Enter a prompt to generate a 3D model:")

if st.button("Generate"):
    if prompt:
        try:
            response = requests.post("http://backend:8000/generate-3d", data={"prompt": prompt})
            if response.status_code == 200:
                # Create the output directory if it doesn't exist
                output_dir = "/home/hpadmin/HPE-Step1X-3D/output"
                os.makedirs(output_dir, exist_ok=True)

                # Save the received file
                file_name = response.headers["content-disposition"].split("filename=")[1]
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(response.content)

                st.success(f"Generated 3D model: {file_name}")
                st.download_button(
                    label="Download PLY file",
                    data=response.content,
                    file_name=file_name,
                    mime="application/octet-stream",
                )
            else:
                st.error(f"Error: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")
    else:
        st.warning("Please enter a prompt.")
