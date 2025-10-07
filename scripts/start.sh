#!/bin/bash

# Start Step1X-3D Services
# Run this script ON THE UBUNTU SERVER

echo "🚀 Starting Step1X-3D services..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy env.example to .env and configure it:"
    echo "  cp env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check if HF_TOKEN is configured
if ! grep -q "HF_TOKEN=hf_" .env; then
    echo "⚠️  Warning: HuggingFace token not configured in .env"
    echo "Please edit .env and add your token:"
    echo "  nano .env"
    echo "  # Add: HF_TOKEN=hf_your_token_here"
fi

# Start backend service
sudo systemctl start step1x3d-backend.service

# Wait for backend to start
sleep 3

# Start frontend service
sudo systemctl start step1x3d-frontend.service

# Wait for services to fully start
sleep 5

echo "✅ Services started"
echo ""
echo "Access URLs:"
echo "  Frontend: http://$(hostname -I | awk '{print $1}'):8501"
echo "  Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo "  API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Check status: ./scripts/status.sh"
echo "View logs: ./scripts/logs.sh"
