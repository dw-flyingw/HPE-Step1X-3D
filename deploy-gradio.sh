#!/bin/bash
# Deploy Step1X-3D with Gradio (Self-Hosted)

echo "=========================================="
echo "Deploy Step1X-3D with Gradio"
echo "=========================================="
echo ""
echo "This deploys a simple Gradio interface"
echo "with automatic UI generation."
echo ""

# Stop any existing services
docker compose down

echo "Building Gradio backend..."
echo "This will take 10-15 minutes (downloading models)..."
echo ""

docker compose build gradio

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Starting Gradio interface..."
    docker compose up -d gradio
    
    echo ""
    echo "=========================================="
    echo "✅ Gradio Interface Running!"
    echo "=========================================="
    echo ""
    echo "Access the UI at:"
    echo "  http://localhost:7860"
    echo "  http://$(hostname -I | awk '{print $1}'):7860"
    echo ""
    echo "Monitor logs:"
    echo "  docker compose logs -f gradio"
    echo ""
    echo "Stop service:"
    echo "  docker compose down"
    echo ""
    
    sleep 5
    echo "Showing logs (Ctrl+C to exit, service keeps running)..."
    docker compose logs -f gradio
else
    echo ""
    echo "❌ Build failed"
    exit 1
fi

