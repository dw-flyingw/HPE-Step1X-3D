#!/bin/bash
# Run minimal Docker setup (fallback if HF Space images aren't available)

echo "=========================================="
echo "Minimal Docker Setup"
echo "=========================================="
echo ""
echo "This creates a minimal container with:"
echo "  - Gradio UI"
echo "  - PyTorch + CUDA"
echo "  - HuggingFace libraries"
echo ""
echo "Note: May still show info page about using HF Space/Endpoints"
echo "      if the step1x3d_geometry package isn't available."
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

echo "Building minimal Docker image..."
docker compose -f docker-compose-minimal.yml build

echo ""
echo "Starting container..."
docker compose -f docker-compose-minimal.yml up -d

echo ""
echo "✅ Container started"
echo ""
echo "Access at: http://$(hostname -I | awk '{print $1}'):7860"
echo ""
echo "Check logs:"
echo "  docker compose -f docker-compose-minimal.yml logs -f"
echo ""

