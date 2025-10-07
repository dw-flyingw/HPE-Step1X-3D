#!/bin/bash
# Setup Step1X-3D Inference System
# Run this once on your Ubuntu server

set -e

echo "=========================================="
echo "Step1X-3D Setup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    echo "   Install: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
echo "✅ Python $PYTHON_VERSION"

# Check uv
if ! command -v uv &> /dev/null; then
    echo "📥 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "❌ uv installation failed"
        exit 1
    fi
fi

echo "✅ uv $(uv --version)"

echo ""
echo "Step 1: Setting up backend..."
cd backend
uv venv

# Install dependencies from pyproject.toml
uv pip install --system \
    fastapi \
    "uvicorn[standard]" \
    python-multipart \
    python-dotenv \
    pillow \
    requests

cd ..
echo "✅ Backend dependencies installed"

echo ""
echo "Step 2: Setting up frontend..."
cd frontend
uv venv

# Install dependencies from pyproject.toml
uv pip install --system \
    streamlit \
    requests \
    pillow \
    python-dotenv

cd ..
echo "✅ Frontend dependencies installed"

echo ""
echo "Step 3: Creating directories..."
mkdir -p output logs
chmod 755 output logs
echo "✅ Directories created"

echo ""
echo "Step 4: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your HuggingFace token!"
    echo "   Get token from: https://huggingface.co/settings/tokens"
else
    echo "✅ .env already exists"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your HF_TOKEN"
echo "   nano .env"
echo ""
echo "2. Start the services:"
echo "   ./start.sh"
echo ""
echo "3. Access the UI:"
echo "   http://localhost:8501"
echo ""

