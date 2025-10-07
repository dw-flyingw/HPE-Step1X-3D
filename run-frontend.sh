#!/bin/bash
# Run Streamlit frontend natively (no Docker)

set -e

echo "=========================================="
echo "Starting Streamlit Frontend"
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

# Install streamlit if not already installed
if ! pip show streamlit &> /dev/null; then
    echo "Installing Streamlit..."
    pip install streamlit
fi

echo "✅ Environment ready"
echo ""
echo "Starting Streamlit frontend..."
echo ""
echo "Access the UI at:"
echo "  http://localhost:8501"
echo "  http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Streamlit app
streamlit run frontend/app_streamlit.py --server.port 8501 --server.address 0.0.0.0

