#!/bin/bash
# Quick fix script for the remote server
# This script updates requirements.txt and rebuilds the backend

set -e

echo "======================================"
echo "Quick Fix for Compatibility Issue"
echo "======================================"
echo ""

# Backup the old requirements.txt
if [ -f backend/requirements.txt ]; then
    cp backend/requirements.txt backend/requirements.txt.backup
    echo "✓ Backed up old requirements.txt"
fi

# Update requirements.txt with compatible versions
cat > backend/requirements.txt << 'REQEOF'
fastapi
uvicorn[standard]
trimesh
torch==2.3.1
torchvision==0.18.1
torchaudio==2.3.1
diffusers==0.30.3
transformers==4.42.4
accelerate==0.33.0
bitsandbytes
python-multipart
Jinja2
einops
pytorch-lightning==2.3.3
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
REQEOF

echo "✓ Updated requirements.txt with compatible versions"
echo ""
echo "Changes:"
echo "  - PyTorch: 2.1.0 → 2.3.1 (required for Step1X-3D's torch.amp API)"
echo "  - Transformers: latest → 4.42.4"
echo "  - Diffusers: latest → 0.30.3"
echo "  - Accelerate: latest → 0.33.0"
echo "  - PyTorch Lightning: latest → 2.3.3"
echo "  - Added specific versions for stability"
echo ""

# Stop backend
echo "Stopping backend container..."
docker compose down backend

# Rebuild with no cache
echo ""
echo "Rebuilding backend (this will take a few minutes)..."
docker compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful! Starting backend..."
    docker compose up -d backend
    
    sleep 3
    
    echo ""
    echo "Backend status:"
    docker compose ps backend
    
    echo ""
    echo "======================================"
    echo "✅ Fix applied successfully!"
    echo "======================================"
    echo ""
    echo "Monitor logs with:"
    echo "  docker compose logs -f backend"
else
    echo ""
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi

