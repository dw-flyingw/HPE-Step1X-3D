#!/bin/bash
# Fix missing dependencies for Step1X-3D

echo "=========================================="
echo "Adding Missing Step1X-3D Dependencies"
echo "=========================================="
echo ""
echo "Adding: jaxtyping, typeguard, opencv-python-headless"
echo ""

cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
python-multipart
python-dotenv
pillow

# Step1X-3D core dependencies
torch==2.5.1
torchvision==0.20.1
transformers==4.46.3
diffusers==0.30.3
accelerate==0.33.0
trimesh
einops
omegaconf
safetensors==0.4.1
huggingface-hub==0.24.5

# Step1X-3D additional dependencies
pytorch-lightning==2.4.0
timm
pymeshlab
numpy<2.0.0
opencv-python-headless
jaxtyping
typeguard
EOF

echo "✅ Updated requirements.txt with all dependencies"
echo ""
echo "Rebuilding (fast with cache)..."

docker compose down backend
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
    echo "❌ Build failed"
    exit 1
fi

