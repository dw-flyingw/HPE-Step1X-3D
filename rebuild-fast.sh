#!/bin/bash
# Fast Rebuild Script - Uses Docker cache
# Use this when you only changed code (app.py), NOT dependencies

echo "=========================================="
echo "Fast Backend Rebuild (with cache)"
echo "=========================================="
echo ""
echo "Use this when:"
echo "  ✅ You changed app.py or other code"
echo "  ✅ Dependencies in requirements.txt are unchanged"
echo ""
echo "DO NOT use this when:"
echo "  ❌ You changed requirements.txt"
echo "  ❌ You're fixing dependency version issues"
echo ""

read -p "Continue with cached build? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Aborted. Use ./rebuild-backend.sh for full rebuild."
    exit 0
fi

echo "Stopping backend..."
docker compose down backend

echo ""
echo "Building (with cache - should be fast!)..."
docker compose build backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Starting backend..."
    docker compose up -d backend
    
    sleep 2
    echo ""
    echo "Backend logs:"
    docker compose logs --tail=50 backend
    
    echo ""
    echo "✅ Backend restarted. Follow logs with:"
    echo "   docker compose logs -f backend"
else
    echo ""
    echo "❌ Build failed."
    exit 1
fi

