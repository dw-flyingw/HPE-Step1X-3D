# build (10-15 min on first run)
docker build -t step1x3d-streamlit .


docker run --rm -it --gpus all \
  -p 8501:8501 \
  -v ~/step1x3d_outputs:/outputs \
  step1x3d-streamlit
