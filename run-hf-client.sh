#!/bin/bash
# Run HuggingFace Inference Client

set -e

echo "=========================================="
echo "Starting HF Inference Client"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo ""
    echo "Please create .env with:"
    echo "  HF_TOKEN=your_token_here"
    echo "  HF_ENDPOINT_URL=your_endpoint_url_here"
    echo ""
    echo "See HF_INFERENCE_ENDPOINTS_GUIDE.md for setup."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "   Run ./setup-hf-client.sh first"
    exit 1
fi

echo "✅ Environment ready"
echo ""
echo "Starting Gradio client..."
echo ""
echo "Access the UI at:"
echo "  http://localhost:7860"
echo "  http://$(hostname -I | awk '{print $1}'):7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the client
python3 client/gradio_client.py

