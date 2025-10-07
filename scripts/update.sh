#!/bin/bash

# Step1X-3D Update Script
# Run this script ON THE UBUNTU SERVER after git pull to update dependencies

set -e

echo "🔄 Updating Step1X-3D..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Get current directory
PROJECT_DIR=$(pwd)
print_status "Project directory: $PROJECT_DIR"

# Make sure uv is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Stop services
print_status "Stopping services..."
./scripts/stop.sh 2>/dev/null || true
sleep 2

# Update backend dependencies
print_status "Updating backend dependencies..."
cd "$PROJECT_DIR/backend"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    uv pip install -e .
    deactivate
    print_success "Backend dependencies updated"
else
    print_status "Backend virtual environment not found, running full install..."
    cd "$PROJECT_DIR"
    ./scripts/install.sh
    exit 0
fi

# Update frontend dependencies
print_status "Updating frontend dependencies..."
cd "$PROJECT_DIR/frontend"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    uv pip install -r requirements.txt
    deactivate
    print_success "Frontend dependencies updated"
else
    print_status "Frontend virtual environment not found, running full install..."
    cd "$PROJECT_DIR"
    ./scripts/install.sh
    exit 0
fi

# Update systemd services if needed
print_status "Updating systemd services..."
cd "$PROJECT_DIR"
sudo systemctl daemon-reload

# Start services
print_status "Starting services..."
./scripts/start.sh

# Check status
sleep 5
./scripts/status.sh

print_success "🎉 Update complete!"
echo ""
echo "Services have been restarted with the latest code."
