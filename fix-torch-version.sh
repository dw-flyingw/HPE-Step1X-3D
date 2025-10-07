#!/bin/bash
# Emergency fix script for torch version issue
# Run this on the remote server to force torch 2.3.1 installation

set -e

echo "=========================================="
echo "Emergency Torch Version Fix"
echo "=========================================="
echo ""

echo "Step 1: Verifying requirements.txt..."
if grep -q "torch==2.3.1" backend/requirements.txt; then
    echo "✅ requirements.txt has torch==2.3.1"
else
    echo "❌ requirements.txt does NOT have torch==2.3.1"
    echo "   Updating now..."
    
    # Backup
    cp backend/requirements.txt backend/requirements.txt.old 2>/dev/null || true
    
    # Update
    cat > backend/requirements.txt << 'EOF'
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
EOF
    echo "✅ Updated requirements.txt"
fi

echo ""
echo "Step 2: Stopping backend..."
docker compose down backend

echo ""
echo "Step 3: Removing old images and containers..."
# Remove the backend image to force complete rebuild
docker rmi hpe-step1x-3d-backend 2>/dev/null || true
docker rmi $(docker images -q 'hpe-step1x-3d*') 2>/dev/null || true

echo "✅ Cleaned up old images"

echo ""
echo "Step 4: Building with NO CACHE (this is critical!)..."
echo "This will take 10-20 minutes. Please be patient."
echo ""

# Build with absolutely no cache
DOCKER_BUILDKIT=1 docker compose build --no-cache --pull backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    # Verify torch version in the image
    echo "Step 5: Verifying torch version in container..."
    TORCH_VERSION=$(docker run --rm hpe-step1x-3d-backend python3 -c "import torch; print(torch.__version__)" 2>/dev/null || echo "unknown")
    
    if [[ "$TORCH_VERSION" == 2.3.* ]]; then
        echo "✅ Torch $TORCH_VERSION confirmed in container!"
    else
        echo "⚠️  Warning: Torch version is $TORCH_VERSION (expected 2.3.x)"
        echo "   The container may still have issues."
    fi
    
    echo ""
    echo "Step 6: Starting backend..."
    docker compose up -d backend
    
    echo ""
    echo "✅ Backend started. Monitoring logs..."
    echo "   (Press Ctrl+C to exit logs, container will keep running)"
    echo ""
    sleep 3
    docker compose logs -f backend
else
    echo ""
    echo "❌ Build failed. Check errors above."
    exit 1
fi

