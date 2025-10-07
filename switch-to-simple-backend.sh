#!/bin/bash
# Switch from complex backend to simplified backend

echo "=========================================="
echo "Switch to Simplified Backend"
echo "=========================================="
echo ""
echo "This will replace the complex 750+ line backend"
echo "with a simple 180-line version that uses official pipelines."
echo ""
echo "Benefits:"
echo "  ✅ 4x less code (750 → 180 lines)"
echo "  ✅ Uses official Step1X-3D APIs"
echo "  ✅ Easier to maintain"
echo "  ✅ Supports texture generation"
echo "  ✅ Follows official documentation"
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Step 1: Backing up current app.py..."
if [ -f "backend/app.py" ]; then
    cp backend/app.py backend/app_old_complex.py
    echo "✅ Backed up to backend/app_old_complex.py"
else
    echo "⚠️  backend/app.py not found"
fi

echo ""
echo "Step 2: Replacing with simplified version..."
if [ -f "backend/app_simple.py" ]; then
    cp backend/app_simple.py backend/app.py
    echo "✅ Copied app_simple.py to app.py"
else
    echo "❌ backend/app_simple.py not found!"
    echo "   Make sure you've transferred all files from local machine."
    exit 1
fi

echo ""
echo "Step 3: Updating requirements.txt..."
# Requirements are already updated in the file

echo ""
echo "Step 4: Rebuilding backend..."
docker compose down backend

echo ""
echo "Building with simplified backend..."
docker compose build backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Step 5: Starting backend..."
    docker compose up -d backend
    
    sleep 3
    echo ""
    echo "=========================================="
    echo "✅ Switched to Simplified Backend!"
    echo "=========================================="
    echo ""
    echo "New API Endpoints:"
    echo "  GET  /                      - Health check"
    echo "  POST /generate-geometry     - Generate untextured 3D (image input)"
    echo "  POST /generate-textured     - Generate textured 3D (image input)"
    echo ""
    echo "Example usage:"
    echo "  curl -X POST http://localhost:8000/generate-textured \\"
    echo "    -F 'image=@input.png' \\"
    echo "    -F 'guidance_scale=7.5' \\"
    echo "    -F 'num_inference_steps=50' \\"
    echo "    -o output.glb"
    echo ""
    echo "Monitor logs:"
    echo "  docker compose logs -f backend"
    echo ""
else
    echo ""
    echo "❌ Build failed. Restoring old backend..."
    if [ -f "backend/app_old_complex.py" ]; then
        cp backend/app_old_complex.py backend/app.py
        echo "✅ Restored old backend"
    fi
    exit 1
fi

