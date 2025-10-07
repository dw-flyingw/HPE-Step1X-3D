#!/bin/bash
# Run HuggingFace Space Docker Image Locally
# Uses the official Space's pre-built Docker image on your GPU

set -e

echo "=========================================="
echo "Run HuggingFace Space Locally"
echo "=========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "   Install: https://docs.docker.com/engine/install/"
    exit 1
fi

echo "✅ Docker found"

# Check GPU
if ! docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "⚠️  Warning: GPU not accessible in Docker"
    echo "   Install nvidia-container-toolkit"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ GPU accessible"
fi

echo ""
echo "=========================================="
echo "Step 1: Login to HuggingFace Registry"
echo "=========================================="
echo ""
echo "You need a HuggingFace account and token."
echo "Get your token from: https://huggingface.co/settings/tokens"
echo ""

read -p "HuggingFace Username: " HF_USERNAME
read -sp "HuggingFace Token: " HF_TOKEN
echo ""

echo ""
echo "Logging in to registry.hf.space..."
echo "$HF_TOKEN" | docker login registry.hf.space -u "$HF_USERNAME" --password-stdin

if [ $? -ne 0 ]; then
    echo "❌ Login failed"
    exit 1
fi

echo "✅ Logged in successfully"

echo ""
echo "=========================================="
echo "Step 2: Pull Space Docker Image"
echo "=========================================="
echo ""
echo "Choose a Space to run:"
echo "1. stepfun-ai/Step1X-3D (official)"
echo "2. cavargas10/Step1X-TextureGeneration"
echo "3. minhtung/Step1X-3D"
echo "4. Custom Space name"
echo ""
read -p "Enter choice [1-4]: " SPACE_CHOICE

case $SPACE_CHOICE in
    1)
        SPACE_IMAGE="registry.hf.space/stepfun-ai-step1x-3d:latest"
        ;;
    2)
        SPACE_IMAGE="registry.hf.space/cavargas10-step1x-texturegeneration:latest"
        ;;
    3)
        SPACE_IMAGE="registry.hf.space/minhtung-step1x-3d:latest"
        ;;
    4)
        read -p "Enter Space name (format: username-spacename): " CUSTOM_SPACE
        SPACE_IMAGE="registry.hf.space/${CUSTOM_SPACE}:latest"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Pulling $SPACE_IMAGE..."
echo "This may take 5-10 minutes..."
echo ""

docker pull "$SPACE_IMAGE"

if [ $? -ne 0 ]; then
    echo "❌ Failed to pull image"
    echo ""
    echo "This could mean:"
    echo "1. The Space doesn't have Docker support"
    echo "2. The Space name is incorrect"
    echo "3. You don't have access to the Space"
    echo ""
    echo "Try visiting the Space page and clicking 'Run with Docker'"
    exit 1
fi

echo "✅ Image pulled successfully"

echo ""
echo "=========================================="
echo "Step 3: Run the Container"
echo "=========================================="
echo ""

# Stop and remove existing container if it exists
docker rm -f step1x3d 2>/dev/null || true

# Create output directory
mkdir -p output

# Run the container
echo "Starting container..."
docker run -d \
    --name step1x3d \
    --gpus all \
    -p 7860:7860 \
    -v "$(pwd)/output:/app/output" \
    "$SPACE_IMAGE"

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container"
    exit 1
fi

echo "✅ Container started"

echo ""
echo "=========================================="
echo "✅ Success! Space is Running"
echo "=========================================="
echo ""
echo "Access the UI at:"
echo "  http://localhost:7860"
echo "  http://$(hostname -I | awk '{print $1}'):7860"
echo ""
echo "Container name: step1x3d"
echo ""
echo "Useful commands:"
echo "  View logs:    docker logs -f step1x3d"
echo "  Stop:         docker stop step1x3d"
echo "  Start:        docker start step1x3d"
echo "  Restart:      docker restart step1x3d"
echo "  Remove:       docker rm -f step1x3d"
echo ""
echo "The container is running in the background."
echo "It may take 2-5 minutes to load models on first run."
echo ""
echo "Check logs for startup progress:"
echo "  docker logs -f step1x3d"
echo ""

