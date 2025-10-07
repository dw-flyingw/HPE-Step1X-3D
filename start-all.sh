#!/bin/bash
# Start both backend and frontend (No Docker)
# Run this on your Ubuntu server

set -e

echo "=========================================="
echo "Starting Step1X-3D Backend & Frontend"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup-native.sh"
    exit 1
fi

# Check if Step1X-3D exists
if [ ! -d "Step1X-3D" ]; then
    echo "❌ Step1X-3D repository not found!"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup-native.sh"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/Step1X-3D"

# Install streamlit if needed
if ! pip show streamlit &> /dev/null; then
    echo "Installing Streamlit..."
    pip install streamlit gradio-client
fi

echo "✅ Environment ready"
echo ""

# Start backend in background
echo "Starting Backend (Gradio) on port 7860..."
nohup python3 backend/app_gradio.py > logs/gradio.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > logs/gradio.pid
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to initialize
sleep 3

# Start frontend in background
echo "Starting Frontend (Streamlit) on port 8501..."
nohup streamlit run frontend/app_streamlit.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    > logs/streamlit.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > logs/streamlit.pid
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "✅ Both services started!"
echo "=========================================="
echo ""
echo "Access the services:"
echo "  Backend (Gradio):    http://$(hostname -I | awk '{print $1}'):7860"
echo "  Frontend (Streamlit): http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "View logs:"
echo "  Backend:  tail -f logs/gradio.log"
echo "  Frontend: tail -f logs/streamlit.log"
echo ""
echo "Stop services:"
echo "  ./stop-all.sh"
echo ""
echo "Note: Backend may take 2-5 minutes to load models on first run."
echo "      Check logs if not accessible immediately."
echo ""

