#!/bin/bash
# Stop Gradio background service

if [ -f "logs/gradio.pid" ]; then
    PID=$(cat logs/gradio.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping Gradio (PID: $PID)..."
        kill $PID
        rm logs/gradio.pid
        echo "✅ Gradio stopped"
    else
        echo "⚠️  Process $PID not running"
        rm logs/gradio.pid
    fi
else
    echo "❌ PID file not found"
    echo "   Manually check: ps aux | grep app_gradio"
fi

