#!/bin/bash
# Final fix: Upgrade to PyTorch 2.5.1 for torch.amp.custom_fwd support

set -e

echo "=========================================="
echo "Final Fix: Upgrading to PyTorch 2.5.1"
echo "=========================================="
echo ""
echo "Why: Step1X-3D uses torch.amp.custom_fwd(device_type='cuda')"
echo "     This API was introduced in PyTorch 2.4+"
echo "     PyTorch 2.3.1 still uses the old torch.cuda.amp API"
echo ""

echo "Updating requirements.txt to PyTorch 2.5.1..."

cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
trimesh
torch==2.5.1
torchvision==0.20.1
torchaudio==2.5.1
diffusers==0.30.3
transformers==4.42.4
accelerate==0.33.0
bitsandbytes
python-multipart
Jinja2
einops
pytorch-lightning==2.4.0
omegaconf
jaxtyping
typeguard
mosaicml-streaming==0.11.0
timm
pymeshlab
wandb
rembg
onnxruntime
beautifulsoup4
python-dotenv
safetensors==0.4.1
huggingface-hub==0.24.5
numpy<2.0.0
EOF

echo "✅ Updated to PyTorch 2.5.1"
echo ""

echo "Stopping backend..."
docker compose down backend

echo ""
echo "Removing old images..."
docker rmi $(docker images -q '*backend*') -f 2>/dev/null || true

echo ""
echo "Building with PyTorch 2.5.1 (10-20 minutes)..."
DOCKER_BUILDKIT=1 docker compose build --no-cache --pull backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    echo "Verifying PyTorch version..."
    TORCH_VERSION=$(docker run --rm hpe-step1x-3d-backend python3 -c "import torch; print(torch.__version__)" 2>/dev/null | tail -1)
    echo "   Installed: $TORCH_VERSION"
    
    echo ""
    echo "Verifying torch.amp.custom_fwd exists..."
    HAS_API=$(docker run --rm hpe-step1x-3d-backend python3 -c "import torch; print(hasattr(torch.amp, 'custom_fwd'))" 2>/dev/null | tail -1)
    if [ "$HAS_API" = "True" ]; then
        echo "   ✅ torch.amp.custom_fwd API available!"
    else
        echo "   ❌ torch.amp.custom_fwd still missing!"
    fi
    
    echo ""
    echo "Starting backend..."
    docker compose up -d backend
    
    echo ""
    echo "✅ Backend started. Monitoring logs..."
    echo "   Watch for successful startup (no torch.amp errors)"
    echo ""
    sleep 3
    docker compose logs -f backend
else
    echo ""
    echo "❌ Build failed."
    exit 1
fi

