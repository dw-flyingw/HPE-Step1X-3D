#!/bin/bash
# Quick Restart Script - NO rebuild
# Use when you just want to restart the container (no code changes)

echo "=========================================="
echo "Quick Backend Restart (no rebuild)"
echo "=========================================="
echo ""

docker compose restart backend

echo ""
echo "✅ Backend restarted"
echo ""
echo "Follow logs with:"
echo "  docker compose logs -f backend"
echo ""

# Show recent logs
docker compose logs --tail=30 backend

