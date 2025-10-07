#!/bin/bash
# Try pulling from community Spaces that may have Docker support

echo "Trying community Spaces..."
echo ""

SPACES=(
    "cavargas10-step1x-texturegeneration"
    "minhtung-step1x-3d"
    "ginigen-3d-llama"
)

for SPACE in "${SPACES[@]}"; do
    echo "Trying: $SPACE"
    docker pull "registry.hf.space/$SPACE:latest" 2>&1 | head -5
    
    if [ $? -eq 0 ]; then
        echo "✅ Found working Space: $SPACE"
        echo ""
        echo "Run it with:"
        echo "  docker run -d --name step1x3d --gpus all -p 7860:7860 registry.hf.space/$SPACE:latest"
        exit 0
    else
        echo "❌ Not available"
        echo ""
    fi
done

echo "None of the Spaces have Docker images available."
echo ""
echo "Alternative: Use the minimal self-hosted setup instead."
echo "See: ./run-minimal-docker.sh"

