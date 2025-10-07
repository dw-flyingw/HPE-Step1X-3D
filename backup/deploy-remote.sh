#!/bin/bash
# Complete deployment script for remote Ubuntu server
# Run this after transferring files to the server

set -e

echo "=========================================="
echo "Step1X-3D Complete Deployment"
echo "=========================================="
echo "Server: $(hostname)"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    echo "   Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
echo "✅ Python $PYTHON_VERSION"

# Step 2: Install uv if needed
echo ""
echo "Step 2: Checking uv..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "❌ uv installation failed"
        exit 1
    fi
fi
echo "✅ uv installed"

# Step 3: Clean old installations
echo ""
echo "Step 3: Cleaning old virtual environments..."
rm -rf backend/.venv frontend/.venv backend/__pycache__ frontend/__pycache__
rm -f backend/*.pyc frontend/*.pyc backend/app_old*.py
echo "✅ Cleaned"

# Step 4: Run setup
echo ""
echo "Step 4: Running setup..."
chmod +x setup.sh
./setup.sh

if [ $? -ne 0 ]; then
    echo "❌ Setup failed"
    exit 1
fi

# Step 5: Configure .env
echo ""
echo "=========================================="
echo "Step 5: Configuration"
echo "=========================================="
echo ""

if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo ""
    echo "You need a HuggingFace token for the Inference API."
    echo "Get one from: https://huggingface.co/settings/tokens"
    echo ""
    read -p "Enter your HuggingFace token (or press Enter to configure later): " HF_TOKEN_INPUT
    
    if [ -z "$HF_TOKEN_INPUT" ]; then
        echo "Skipping token configuration for now..."
        cp env.template .env
        echo "⚠️  You'll need to edit .env and add your HF_TOKEN before starting!"
    else
        cat > .env << EOF
# HuggingFace Configuration
HF_TOKEN=$HF_TOKEN_INPUT

# Backend Configuration
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000

# Frontend Configuration
FRONTEND_PORT=8501
EOF
        echo "✅ .env configured with your token"
    fi
else
    echo "✅ .env already exists"
fi

# Step 6: Start services
echo ""
echo "=========================================="
echo "Step 6: Starting Services"
echo "=========================================="
echo ""

read -p "Start the services now? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    chmod +x start.sh
    ./start.sh
    
    echo ""
    echo "=========================================="
    echo "✅ Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "Access the UI:"
    echo "  http://localhost:8501"
    echo "  http://$(hostname -I | awk '{print $1}'):8501"
    echo ""
    echo "Backend API:"
    echo "  http://localhost:8000"
    echo ""
    echo "Useful commands:"
    echo "  ./status.sh      - Check service status"
    echo "  ./stop.sh        - Stop services"
    echo "  ./start.sh       - Start services"
    echo "  tail -f logs/*.log - View logs"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "To start the services:"
    echo "  ./start.sh"
    echo ""
    echo "Remember to add your HF_TOKEN to .env if you haven't:"
    echo "  nano .env"
    echo ""
fi

