#!/bin/bash

# One-Command Deployment Script for Step1X-3D
# Deploys from local MacBook to remote Ubuntu server

set -e

# Configuration
REMOTE_USER="hpadmin"
REMOTE_HOST="sut73"
REMOTE_PATH="~/HPE-Step1X-3D"
LOCAL_PATH="/Users/dave/AI/HPE/HPE-Step1X-3D"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Step1X-3D One-Command Deployment${NC}"
echo ""

# Step 1: Copy files to server
echo -e "${BLUE}[1/3]${NC} Copying files to remote server..."
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.venv/' \
    --exclude='backup/' \
    --exclude='output/logs/' \
    "$LOCAL_PATH/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

echo -e "${GREEN}✅ Files copied successfully${NC}"
echo ""

# Step 2: Setup on remote server
echo -e "${BLUE}[2/3]${NC} Setting up on remote server..."
ssh "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
cd ~/HPE-Step1X-3D

# Make scripts executable
chmod +x scripts/*.sh

# Check if this is first-time setup
if [ ! -d "backend/.venv" ] || [ ! -d "frontend/.venv" ]; then
    echo "🔧 Running initial setup..."
    ./scripts/setup.sh
else
    echo "📦 Updating dependencies..."
    cd backend && source .venv/bin/activate && uv pip install -e . && cd ..
    cd frontend && source .venv/bin/activate && uv pip install -r requirements.txt && cd ..
fi
EOF

echo -e "${GREEN}✅ Remote setup completed${NC}"
echo ""

# Step 3: Start services
echo -e "${BLUE}[3/3]${NC} Starting services on remote server..."
ssh "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
cd ~/HPE-Step1X-3D

# Check if .env exists and has HF_TOKEN
if [ ! -f ".env" ] || ! grep -q "HF_TOKEN=hf_" .env; then
    echo "⚠️  Please configure your HuggingFace token:"
    echo "   ssh $REMOTE_USER@$REMOTE_HOST"
    echo "   cd ~/HPE-Step1X-3D"
    echo "   nano .env"
    echo "   # Add: HF_TOKEN=hf_your_token_here"
    echo ""
    echo "Then run: ./scripts/start.sh"
    exit 0
fi

# Start services
echo "🚀 Starting services..."
./scripts/start.sh

# Wait for services to start
sleep 10

# Check status
echo ""
echo "📊 Service Status:"
./scripts/status.sh

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🌐 Access Information:"
echo "   Frontend: http://$SERVER_IP:8501"
echo "   Backend:  http://$SERVER_IP:8000"
echo "   API Docs: http://$SERVER_IP:8000/docs"
echo ""
echo "🔧 Management:"
echo "   Status:  ssh $REMOTE_USER@$REMOTE_HOST 'cd ~/HPE-Step1X-3D && ./scripts/status.sh'"
echo "   Logs:    ssh $REMOTE_USER@$REMOTE_HOST 'cd ~/HPE-Step1X-3D && ./scripts/logs.sh'"
echo "   Stop:    ssh $REMOTE_USER@$REMOTE_HOST 'cd ~/HPE-Step1X-3D && ./scripts/stop.sh'"
EOF

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Access the frontend at the URL shown above"
echo "2. Test 3D generation with a sample image"
echo "3. Monitor GPU usage: ssh $REMOTE_USER@$REMOTE_HOST 'watch nvidia-smi'"
echo ""
echo -e "${BLUE}Happy 3D generating! 🎨${NC}"
