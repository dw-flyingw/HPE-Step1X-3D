#!/bin/bash
# Full Rebuild Script - NO cache
# Use this ONLY when you changed requirements.txt or need to fix dependency issues

echo "=========================================="
echo "Full Backend Rebuild (NO cache)"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will take 10-20 minutes!"
echo ""
echo "Use this ONLY when:"
echo "  ✅ You changed requirements.txt (dependency versions)"
echo "  ✅ You're fixing dependency/version issues"
echo "  ✅ Cache is causing problems"
echo ""
echo "For code-only changes, use ./rebuild-fast.sh instead (much faster!)"
echo ""

read -p "Continue with FULL rebuild (10-20 min)? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. Use ./rebuild-fast.sh for quick code changes."
    exit 0
fi

echo ""
echo "Stopping backend..."
docker compose down backend

echo ""
echo "Removing old images..."
docker rmi $(docker images -q '*backend*') -f 2>/dev/null || true

echo ""
echo "Building with NO cache..."
echo "This will take 10-20 minutes. Go get coffee ☕"
echo ""

DOCKER_BUILDKIT=1 docker compose build --no-cache --pull backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Starting backend..."
    docker compose up -d backend
    
    sleep 3
    echo ""
    echo "✅ Backend started. Monitoring logs..."
    docker compose logs -f backend
else
    echo ""
    echo "❌ Build failed."
    exit 1
fi

