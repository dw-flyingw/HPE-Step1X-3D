#!/bin/bash
# Stop both backend and frontend

echo "Stopping Step1X-3D services..."
echo ""

STOPPED=0

# Stop backend
if [ -f "logs/gradio.pid" ]; then
    BACKEND_PID=$(cat logs/gradio.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm logs/gradio.pid
        echo "✅ Backend stopped"
        STOPPED=1
    else
        echo "⚠️  Backend process not running"
        rm logs/gradio.pid
    fi
else
    echo "⚠️  Backend PID file not found"
fi

# Stop frontend
if [ -f "logs/streamlit.pid" ]; then
    FRONTEND_PID=$(cat logs/streamlit.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm logs/streamlit.pid
        echo "✅ Frontend stopped"
        STOPPED=1
    else
        echo "⚠️  Frontend process not running"
        rm logs/streamlit.pid
    fi
else
    echo "⚠️  Frontend PID file not found"
fi

if [ $STOPPED -eq 0 ]; then
    echo ""
    echo "No services were running."
    echo "Check manually: ps aux | grep -E 'app_gradio|streamlit'"
else
    echo ""
    echo "✅ All services stopped"
fi

