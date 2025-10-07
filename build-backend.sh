#!/bin/bash

# Build and Test Script for HPE Step1X-3D Backend
# This script helps verify that the backend Docker image can be built correctly

set -e  # Exit on error

echo "======================================"
echo "HPE Step1X-3D Backend Build Script"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "✓ Docker is running"

# Check if NVIDIA Docker runtime is available
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    echo "✓ NVIDIA GPU support is available"
else
    echo "⚠️  Warning: NVIDIA GPU support may not be available"
    echo "   The backend requires GPU support to run properly"
fi

# Create output directory if it doesn't exist
mkdir -p output
echo "✓ Output directory created/verified"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file with default configuration..."
    cat > .env << 'EOF'
# Backend Configuration
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_PORT=8501

# Output Directory (inside containers)
OUTPUT_DIR=/app/output

# Backend URL (for frontend to connect)
BACKEND_URL=http://backend:8000

# Optional: DICOM Viewer Port (if needed for future features)
DICOM_VIEWER_PORT=8080
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Build the backend image
echo ""
echo "Building backend Docker image..."
echo "This may take several minutes on first build..."
echo ""

docker compose build backend

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ Backend image built successfully!"
    echo "======================================"
    echo ""
    echo "To start the backend service, run:"
    echo "  docker compose up -d backend"
    echo ""
    echo "To view logs:"
    echo "  docker compose logs -f backend"
    echo ""
    echo "To test the API (replace localhost with your server IP if remote):"
    echo "  curl -X POST http://localhost:8000/generate-3d -F 'prompt=a red chair'"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ Backend image build failed"
    echo "======================================"
    echo ""
    echo "Please check the error messages above and:"
    echo "1. Ensure Docker has enough disk space"
    echo "2. Check that all required files are present"
    echo "3. Verify network connectivity for downloading dependencies"
    exit 1
fi

