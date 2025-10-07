#!/bin/bash
# Run Gradio interface natively (no Docker)

set -e

echo "=========================================="
echo "Starting Step1X-3D Gradio Interface"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run ./setup-native.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Step1X-3D exists
if [ ! -d "Step1X-3D" ]; then
    echo "❌ Step1X-3D repository not found!"
    echo "   Run ./setup-native.sh first"
    exit 1
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/Step1X-3D"

echo "✅ Environment ready"
echo ""
echo "Starting Gradio interface..."
echo "This will:"
echo "  1. Load models (2-5 minutes first time)"
echo "  2. Start web server on port 7860"
echo ""
echo "Access the UI at:"
echo "  http://localhost:7860"
echo "  http://$(hostname -I | awk '{print $1}'):7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Gradio app
python3 backend/app_gradio.py

