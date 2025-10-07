#!/bin/bash
# Remote Server Setup Verification Script
# Run this on hpadmin@sut73 before building

echo "======================================"
echo "Remote Server Setup Verification"
echo "Server: $(hostname)"
echo "User: $(whoami)"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Check we're in the right directory
if [[ ! "$(pwd)" == *"HPE-Step1X-3D"* ]]; then
    echo "⚠️  Warning: Not in HPE-Step1X-3D directory"
    echo "   Current: $(pwd)"
    echo "   Expected: ~/HPE-Step1X-3D"
    WARNINGS=$((WARNINGS+1))
fi

echo "1. Checking Step1X-3D code..."
if [ -f "Step1X-3D/step1x3d_geometry/__init__.py" ]; then
    echo "   ✅ Step1X-3D code found"
    
    # Check for key modules
    if [ -d "Step1X-3D/step1x3d_geometry/models" ]; then
        echo "   ✅ models/ module found"
    else
        echo "   ⚠️  models/ module missing"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "   ❌ CRITICAL: Step1X-3D code NOT found!"
    echo ""
    echo "   FIX: Run one of these:"
    echo "   git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D"
    echo "   OR copy from local: rsync -avz /path/to/Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/Step1X-3D/"
    echo ""
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "2. Checking GPU access..."
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "   ✅ GPU accessible via Docker"
    
    # Show GPU info
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1)
    echo "   ℹ️  GPU: $GPU_NAME ($GPU_MEM)"
else
    echo "   ❌ GPU not accessible via Docker"
    echo "   FIX: Check nvidia-container-toolkit installation"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "3. Checking disk space..."
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -lt 20 ]; then
    echo "   ⚠️  Low disk space: ${AVAILABLE}GB free (need 20GB+)"
    echo "   Consider cleaning: docker system prune -a"
    WARNINGS=$((WARNINGS+1))
else
    echo "   ✅ Sufficient disk space: ${AVAILABLE}GB free"
fi

echo ""
echo "4. Checking requirements.txt..."
if [ -f "backend/requirements.txt" ]; then
    if grep -q "torch==2.3.1" backend/requirements.txt; then
        echo "   ✅ requirements.txt updated (torch==2.3.1)"
    else
        echo "   ⚠️  requirements.txt may be outdated"
        echo "   Current torch version: $(grep "^torch==" backend/requirements.txt || echo "not specified")"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "   ❌ requirements.txt NOT found!"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "5. Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    echo "   ✅ docker-compose.yml found"
else
    echo "   ❌ docker-compose.yml NOT found!"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "6. Checking .env file..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ℹ️  .env file missing (will create with defaults)"
    cat > .env << 'EOF'
BACKEND_PORT=8000
FRONTEND_PORT=8501
OUTPUT_DIR=/app/output
BACKEND_URL=http://backend:8000
EOF
    echo "   ✅ .env created"
fi

echo ""
echo "7. Checking output directory..."
if [ -d "output" ]; then
    echo "   ✅ output directory exists"
else
    mkdir -p output
    echo "   ✅ output directory created"
fi
chmod 755 output

echo ""
echo "8. Checking Docker..."
if command -v docker &>/dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "   ✅ Docker installed: $DOCKER_VERSION"
    
    if docker compose version &>/dev/null; then
        COMPOSE_VERSION=$(docker compose version)
        echo "   ✅ Docker Compose available: $COMPOSE_VERSION"
    else
        echo "   ⚠️  'docker compose' command not found"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "   ❌ Docker not installed or not in PATH"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "9. Checking network connectivity..."
if ping -c 1 huggingface.co &>/dev/null; then
    echo "   ✅ Can reach huggingface.co"
else
    echo "   ⚠️  Cannot reach huggingface.co (needed for model downloads)"
    echo "   Models may fail to download on first run"
    WARNINGS=$((WARNINGS+1))
fi

echo ""
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ READY TO BUILD!"
    echo ""
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  $WARNINGS warning(s) - review above, but you can proceed"
    fi
    echo ""
    echo "Next steps:"
    echo "  docker compose build --no-cache backend"
    echo "  docker compose up -d backend"
    echo "  docker compose logs -f backend"
    echo ""
    echo "Expected build time: 10-20 minutes"
    echo "Expected first startup: 10-30 minutes (downloading models)"
else
    echo "❌ CANNOT BUILD - $ERRORS critical error(s) found"
    echo ""
    echo "Fix the errors above, then run this script again."
    echo ""
    exit 1
fi

