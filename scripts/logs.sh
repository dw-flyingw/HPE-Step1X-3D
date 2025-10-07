#!/bin/bash

# View Step1X-3D Service Logs
# Run this script ON THE UBUNTU SERVER

# Parse command line arguments
SERVICE="${1:-both}"

case "$SERVICE" in
    "backend"|"b")
        echo "📋 Backend Logs (Ctrl+C to exit):"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        sudo journalctl -u step1x3d-backend.service -f --no-pager
        ;;
    "frontend"|"f")
        echo "📋 Frontend Logs (Ctrl+C to exit):"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        sudo journalctl -u step1x3d-frontend.service -f --no-pager
        ;;
    "both"|*)
        echo "📋 All Service Logs (Ctrl+C to exit):"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Use: ./scripts/logs.sh [backend|frontend|both]"
        echo ""
        echo "Recent Backend Logs:"
        sudo journalctl -u step1x3d-backend.service -n 20 --no-pager
        echo ""
        echo "Recent Frontend Logs:"
        sudo journalctl -u step1x3d-frontend.service -n 20 --no-pager
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "For live logs, use:"
        echo "  ./scripts/logs.sh backend   # Backend only"
        echo "  ./scripts/logs.sh frontend  # Frontend only"
        ;;
esac
