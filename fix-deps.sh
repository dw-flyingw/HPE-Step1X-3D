#!/bin/bash
# Quick fix: Install missing dependencies

source venv/bin/activate

echo "Installing missing dependencies..."
pip install pytorch-lightning==2.4.0 opencv-python-headless jaxtyping typeguard

echo "✅ Dependencies installed"
echo ""
echo "Now try again:"
echo "  ./run-gradio.sh"

