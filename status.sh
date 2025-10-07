#!/bin/bash
# Check service status

echo "=========================================="
echo "Service Status"
echo "=========================================="
echo ""

# Backend
if [ -f logs/backend.pid ] && ps -p $(cat logs/backend.pid) > /dev/null 2>&1; then
    echo "Backend:  ✅ Running (PID: $(cat logs/backend.pid))"
    echo "          http://localhost:${BACKEND_PORT:-8000}"
else
    echo "Backend:  ❌ Not running"
fi

echo ""

# Frontend
if [ -f logs/frontend.pid ] && ps -p $(cat logs/frontend.pid) > /dev/null 2>&1; then
    echo "Frontend: ✅ Running (PID: $(cat logs/frontend.pid))"
    echo "          http://localhost:${FRONTEND_PORT:-8501}"
else
    echo "Frontend: ❌ Not running"
fi

echo ""
echo "Logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""

