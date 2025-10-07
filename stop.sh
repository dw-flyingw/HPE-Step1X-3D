#!/bin/bash
# Stop both backend and frontend

echo "Stopping services..."

# Stop backend
if [ -f logs/backend.pid ]; then
    PID=$(cat logs/backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        rm logs/backend.pid
        echo "✅ Backend stopped"
    fi
fi

# Stop frontend
if [ -f logs/frontend.pid ]; then
    PID=$(cat logs/frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        rm logs/frontend.pid
        echo "✅ Frontend stopped"
    fi
fi

echo "✅ All services stopped"

