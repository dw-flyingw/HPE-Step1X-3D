#!/bin/bash
# Native Setup for Step1X-3D (No Docker)
# Run this on your remote server

set -e

echo "=========================================="
echo "Step1X-3D Native Setup (No Docker)"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION" != "3.10" ] && [ "$PYTHON_VERSION" != "3.11" ]; then
    echo "⚠️  Warning: Python 3.10 or 3.11 recommended, you have $PYTHON_VERSION"
fi

# Check CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "❌ No NVIDIA GPU detected - this won't work!"
    exit 1
fi

echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "✅ Virtual environment created"
echo ""

echo "Step 2: Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Step 3: Installing PyTorch with CUDA 11.8..."
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118

echo ""
echo "Step 4: Installing Step1X-3D dependencies..."
pip install gradio==4.44.0 \
    transformers==4.46.3 \
    diffusers==0.30.3 \
    accelerate==0.33.0 \
    pillow \
    trimesh \
    einops \
    omegaconf \
    safetensors \
    huggingface-hub \
    timm \
    pymeshlab \
    "numpy<2.0.0" \
    pytorch-lightning==2.4.0 \
    opencv-python-headless \
    jaxtyping \
    typeguard

echo ""
echo "Step 5: Cloning Step1X-3D repository..."
if [ ! -d "Step1X-3D" ]; then
    git clone https://github.com/stepfun-ai/Step1X-3D.git
    echo "✅ Step1X-3D cloned"
else
    echo "✅ Step1X-3D already exists"
fi

echo ""
echo "Step 6: Creating output directory..."
mkdir -p output
chmod 755 output

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the Gradio interface:"
echo "  ./run-gradio.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python3 backend/app_gradio.py"
echo ""

