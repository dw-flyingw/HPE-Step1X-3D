#!/bin/bash
# Quick fix: Add OpenCV dependency

echo "Adding opencv-python-headless to requirements..."

cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
python-multipart
python-dotenv
pillow

# Step1X-3D dependencies
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

# Additional dependencies for Step1X-3D
pytorch-lightning==2.4.0
timm
pymeshlab
numpy<2.0.0
opencv-python-headless
EOF

echo "✅ Updated requirements.txt"
echo ""
echo "Rebuilding backend (should be fast with cache)..."

docker compose down backend
docker compose build backend
docker compose up -d backend

echo ""
echo "Monitoring logs..."
docker compose logs -f backend

