#!/bin/bash
# Check status of backend and frontend

echo "=========================================="
echo "Step1X-3D Services Status"
echo "=========================================="
echo ""

# Check backend
echo "Backend (Gradio - Port 7860):"
if [ -f "logs/gradio.pid" ]; then
    BACKEND_PID=$(cat logs/gradio.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "  ✅ Running (PID: $BACKEND_PID)"
        echo "  Access: http://$(hostname -I | awk '{print $1}'):7860"
    else
        echo "  ❌ Not running (stale PID file)"
    fi
else
    echo "  ❌ Not running"
fi

echo ""

# Check frontend
echo "Frontend (Streamlit - Port 8501):"
if [ -f "logs/streamlit.pid" ]; then
    FRONTEND_PID=$(cat logs/streamlit.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "  ✅ Running (PID: $FRONTEND_PID)"
        echo "  Access: http://$(hostname -I | awk '{print $1}'):8501"
    else
        echo "  ❌ Not running (stale PID file)"
    fi
else
    echo "  ❌ Not running"
fi

echo ""
echo "Logs:"
echo "  Backend:  tail -f logs/gradio.log"
echo "  Frontend: tail -f logs/streamlit.log"
echo ""

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Status:"
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | \
        awk -F', ' '{printf "  GPU %s: %s | GPU: %s%% | Memory: %s/%s MB\n", $1, $2, $3, $4, $5}'
fi

echo ""

