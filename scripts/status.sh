#!/bin/bash

# Check Step1X-3D Service Status
# Run this script ON THE UBUNTU SERVER

echo "📊 Step1X-3D Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Backend status
echo "🔧 Backend Service:"
sudo systemctl status step1x3d-backend.service --no-pager -l | head -n 15
echo ""

# Frontend status
echo "🖥️  Frontend Service:"
sudo systemctl status step1x3d-frontend.service --no-pager -l | head -n 15
echo ""

# GPU status
echo "🎮 GPU Status:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | \
    awk -F', ' '{printf "GPU %s: %s | Memory: %s/%s MB | Utilization: %s%%\n", $1, $2, $3, $4, $5}'
else
    echo "nvidia-smi not available"
fi
echo ""

# Port status
echo "🌐 Port Status:"
if sudo lsof -i :8000 &> /dev/null; then
    echo "✅ Backend (port 8000): LISTENING"
else
    echo "❌ Backend (port 8000): NOT LISTENING"
fi

if sudo lsof -i :8501 &> /dev/null; then
    echo "✅ Frontend (port 8501): LISTENING"
else
    echo "❌ Frontend (port 8501): NOT LISTENING"
fi
echo ""

# Access URLs
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "🔗 Access URLs:"
echo "   Frontend: http://$SERVER_IP:8501"
echo "   Backend:  http://$SERVER_IP:8000"
echo "   API Docs: http://$SERVER_IP:8000/docs"
echo ""
