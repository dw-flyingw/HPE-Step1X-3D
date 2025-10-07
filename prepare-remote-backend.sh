#!/bin/bash
# Comprehensive Backend Preparation Script for Remote Server
# Run this on hpadmin@sut73:~/HPE-Step1X-3D
# This script does EVERYTHING needed to prepare the backend

set -e  # Exit on error

echo "=========================================="
echo "HPE Step1X-3D Backend Preparation"
echo "=========================================="
echo "Server: $(hostname)"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo ""

# Confirm we're in the right place
if [[ ! "$(pwd)" == *"HPE-Step1X-3D"* ]]; then
    echo "⚠️  Warning: You don't appear to be in the HPE-Step1X-3D directory"
    echo "Current directory: $(pwd)"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Step 1: Checking Step1X-3D repository..."
echo "----------------------------------------"
if [ -f "Step1X-3D/step1x3d_geometry/__init__.py" ]; then
    echo "✅ Step1X-3D code already present"
else
    echo "📥 Step1X-3D code not found. Attempting to clone..."
    
    if [ -d "Step1X-3D" ] && [ -z "$(ls -A Step1X-3D)" ]; then
        echo "   Removing empty Step1X-3D directory..."
        rmdir Step1X-3D
    fi
    
    if command -v git &>/dev/null; then
        echo "   Cloning from GitHub..."
        if git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D; then
            echo "✅ Step1X-3D cloned successfully"
        else
            echo "❌ Failed to clone Step1X-3D repository"
            echo ""
            echo "Manual fix required:"
            echo "  1. On your local machine: git clone https://github.com/stepfun-ai/Step1X-3D.git"
            echo "  2. Copy to server: rsync -avz Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/Step1X-3D/"
            echo ""
            exit 1
        fi
    else
        echo "❌ git not found. Cannot clone automatically."
        echo ""
        echo "Manual fix required:"
        echo "  Install git: sudo apt-get install git"
        echo "  Or copy from local machine"
        exit 1
    fi
fi

# Verify Step1X-3D structure
if [ -d "Step1X-3D/step1x3d_geometry/models" ]; then
    echo "✅ Step1X-3D structure verified"
else
    echo "⚠️  Warning: Step1X-3D structure may be incomplete"
fi

echo ""
echo "Step 2: Updating requirements.txt..."
echo "----------------------------------------"
if [ -f "backend/requirements.txt.backup" ]; then
    echo "   Backup already exists, skipping..."
else
    if [ -f "backend/requirements.txt" ]; then
        cp backend/requirements.txt backend/requirements.txt.backup
        echo "✅ Backed up original requirements.txt"
    fi
fi

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

echo "✅ requirements.txt updated with compatible versions"
echo "   Key versions:"
echo "   - PyTorch: 2.3.1 (required for torch.amp API)"
echo "   - Transformers: 4.42.4"
echo "   - Diffusers: 0.30.3"

echo ""
echo "Step 3: Creating .env file..."
echo "----------------------------------------"
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
    cat .env
else
    cat > .env << 'EOF'
BACKEND_PORT=8000
FRONTEND_PORT=8501
OUTPUT_DIR=/app/output
BACKEND_URL=http://backend:8000
EOF
    echo "✅ .env file created with defaults"
    cat .env
fi

echo ""
echo "Step 4: Setting up output directory..."
echo "----------------------------------------"
mkdir -p output
chmod 755 output
echo "✅ output directory ready"

echo ""
echo "Step 5: Verifying Docker setup..."
echo "----------------------------------------"

# Check Docker
if command -v docker &>/dev/null; then
    echo "✅ Docker installed: $(docker --version)"
else
    echo "❌ Docker not found"
    exit 1
fi

# Check Docker Compose
if docker compose version &>/dev/null; then
    echo "✅ Docker Compose: $(docker compose version)"
else
    echo "❌ Docker Compose not available"
    exit 1
fi

# Check GPU
echo "   Checking GPU access..."
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null 2>&1; then
    echo "✅ GPU accessible via Docker"
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)
    echo "   GPU: $GPU_INFO"
else
    echo "⚠️  Warning: GPU not accessible via Docker"
    echo "   The backend requires GPU access to function"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Step 6: Checking disk space..."
echo "----------------------------------------"
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
echo "   Available: ${AVAILABLE}GB"
if [ "$AVAILABLE" -lt 20 ]; then
    echo "⚠️  Warning: Low disk space (need 20GB+)"
    echo "   Consider running: docker system prune -a"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Sufficient disk space"
fi

echo ""
echo "Step 7: Checking network connectivity..."
echo "----------------------------------------"
if ping -c 1 huggingface.co &>/dev/null; then
    echo "✅ Can reach huggingface.co"
else
    echo "⚠️  Warning: Cannot reach huggingface.co"
    echo "   Model downloads may fail on first run"
fi

echo ""
echo "=========================================="
echo "✅ Preparation Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ Step1X-3D code: Present"
echo "  ✅ requirements.txt: Updated (torch 2.3.1)"
echo "  ✅ .env file: Configured"
echo "  ✅ output directory: Ready"
echo "  ✅ Docker: Available"
echo ""
echo "Next Steps:"
echo "----------------------------------------"
echo ""
echo "Option 1: Build and start now (recommended)"
echo "  docker compose build --no-cache backend"
echo "  docker compose up -d backend"
echo "  docker compose logs -f backend"
echo ""
echo "Option 2: Just build (don't start yet)"
echo "  docker compose build --no-cache backend"
echo ""
echo "Option 3: Use the automated build script"
echo "  ./build-backend.sh"
echo ""
echo "Expected Timeline:"
echo "  - Build: 10-20 minutes"
echo "  - First startup: 10-30 minutes (downloading models)"
echo "  - Subsequent starts: 2-5 minutes"
echo ""

# Ask if user wants to build now
read -p "Build the backend now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting build process..."
    echo "This will take 10-20 minutes. Please be patient."
    echo ""
    
    # Stop any existing containers
    docker compose down backend 2>/dev/null || true
    
    # Build
    echo "Building backend image..."
    docker compose build --no-cache backend
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Build successful!"
        echo ""
        read -p "Start the backend now? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            echo "Starting backend..."
            docker compose up -d backend
            
            echo ""
            echo "✅ Backend started!"
            echo ""
            echo "Monitor logs with:"
            echo "  docker compose logs -f backend"
            echo ""
            echo "Check status with:"
            echo "  docker compose ps"
            echo ""
            echo "Note: First startup will take 10-30 minutes to download models."
        fi
    else
        echo ""
        echo "❌ Build failed. Check the errors above."
        exit 1
    fi
else
    echo ""
    echo "Skipping build. Run one of the commands above when ready."
fi

echo ""
echo "=========================================="
echo "Setup script complete!"
echo "=========================================="

