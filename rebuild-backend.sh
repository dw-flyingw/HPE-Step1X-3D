#!/bin/bash

# Rebuild Backend Script
# Use this when you need to rebuild the backend after code changes

set -e  # Exit on error

echo "======================================"
echo "HPE Step1X-3D Backend Rebuild Script"
echo "======================================"
echo ""

# Stop the current backend container
echo "Stopping current backend container..."
docker compose down backend

# Clean up old images (optional, comment out if you want to keep them)
echo "Cleaning up old images..."
docker image prune -f

# Rebuild the backend image with no cache to ensure fresh build
echo ""
echo "Rebuilding backend Docker image (no cache)..."
echo "This may take several minutes..."
echo ""

docker compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ Backend rebuilt successfully!"
    echo "======================================"
    echo ""
    echo "Starting the backend service..."
    docker compose up -d backend
    
    echo ""
    echo "Waiting for backend to start..."
    sleep 5
    
    echo ""
    echo "Backend logs (last 50 lines):"
    docker compose logs --tail=50 backend
    
    echo ""
    echo "======================================"
    echo "To follow logs in real-time:"
    echo "  docker compose logs -f backend"
    echo ""
    echo "To check status:"
    echo "  docker compose ps"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ Backend rebuild failed"
    echo "======================================"
    exit 1
fi

