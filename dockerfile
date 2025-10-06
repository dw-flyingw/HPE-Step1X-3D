# ---------- base image ------------------------------------------------------
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# ---------- system packages -------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential cmake ninja-build \
    python3.10 python3.10-dev python3.10-venv python3-pip \
    && ln -sf python3.10 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# ---------- python venv -----------------------------------------------------
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -U pip setuptools wheel ninja

# ---------- pytorch (needed by almost everything) ---------------------------
RUN pip install \
    torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cu124

# ---------- torch ecosystem (exact matching wheels) ------------------------
RUN pip install --no-cache-dir --no-deps \
    torch==2.5.1+cu124 \
    torchvision==0.20.1+cu124 \
    torchaudio==2.5.1+cu124 \
    -f https://download.pytorch.org/whl/torch_stable.html

# ---------- kaolin (pre-built wheel) ---------------------------------------
RUN pip install kaolin==0.17.0 \
    -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.5.1_cu124.html

# ---------- clone Step1X-3D repo -------------------------------------------
WORKDIR /workspace
RUN git clone --depth 1 https://github.com/stepfun-ai/Step1X-3D.git .

# ---------- python dependencies (no kaolin here!) --------------------------
COPY requirements-lock.txt ./

# ---------- runtime / missing deps ----------------------------------------
RUN pip install pytorch-lightning torchmetrics
RUN pip install --no-build-isolation -r requirements-lock.txt

# ---------- runtime utilities ---------------------------------------------
RUN pip install streamlit

# ---------- build local CUDA extensions -------------------------------------
ENV TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0"
RUN cd step1x3d_texture/custom_rasterizer && python setup.py install && \
    cd ../differentiable_renderer     && python setup.py install

# ---------- streamlit app ----------------------------------------------------
COPY app.py ./app.py
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
