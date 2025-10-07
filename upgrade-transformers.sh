#!/bin/bash
# Upgrade transformers to 4.46.3 for dinov2_with_registers support

echo "=========================================="
echo "Upgrading transformers to 4.46.3"
echo "=========================================="
echo ""
echo "Why: Step1X-3D needs transformers.models.dinov2_with_registers"
echo "     This model was added in transformers 4.45.0"
echo ""

cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
trimesh
torch==2.5.1
torchvision==0.20.1
torchaudio==2.5.1
diffusers==0.30.3
transformers==4.46.3
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

echo "✅ Updated requirements.txt (transformers 4.46.3)"
echo ""

# Since we're just upgrading one package, we can use cached build
echo "Stopping backend..."
docker compose down backend

echo ""
echo "Rebuilding (this will be faster with cache)..."
docker compose build backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    echo "Starting backend..."
    docker compose up -d backend
    
    sleep 3
    echo ""
    echo "Monitoring logs..."
    docker compose logs -f backend
else
    echo ""
    echo "❌ Build failed."
    exit 1
fi

