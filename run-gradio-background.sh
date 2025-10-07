#!/bin/bash
# Run Gradio interface in background (no Docker)

set -e

echo "Starting Step1X-3D Gradio in background..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run ./setup-native.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/Step1X-3D"

# Run in background with nohup
nohup python3 backend/app_gradio.py > logs/gradio.log 2>&1 &
PID=$!

echo "✅ Gradio started in background (PID: $PID)"
echo ""
echo "Access the UI at:"
echo "  http://localhost:7860"
echo "  http://$(hostname -I | awk '{print $1}'):7860"
echo ""
echo "View logs:"
echo "  tail -f logs/gradio.log"
echo ""
echo "Stop service:"
echo "  ./stop-gradio.sh"
echo "  Or: kill $PID"
echo ""

# Save PID
mkdir -p logs
echo $PID > logs/gradio.pid

