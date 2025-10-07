#!/bin/bash

# Step1X-3D Installation Script for Ubuntu Server
# Run this script ON THE UBUNTU SERVER after git pull
# This script sets up the complete environment for local GPU inference

set -e

echo "🚀 Installing Step1X-3D on Ubuntu Server..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Get current directory
PROJECT_DIR=$(pwd)
print_status "Project directory: $PROJECT_DIR"

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    pkg-config \
    libopenblas-dev \
    liblapack-dev \
    libx11-6 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

print_success "System dependencies installed"

# Check NVIDIA GPU and drivers
print_status "Checking NVIDIA GPU and drivers..."
if command -v nvidia-smi &> /dev/null; then
    print_success "NVIDIA drivers found"
    nvidia-smi
else
    print_warning "NVIDIA drivers not found. Installing..."
    sudo apt install -y nvidia-driver-535
    print_warning "NVIDIA drivers installed. Please reboot and run this script again."
    exit 0
fi

# Check CUDA
print_status "Checking CUDA installation..."
if command -v nvcc &> /dev/null; then
    print_success "CUDA found: $(nvcc --version | grep release)"
else
    print_warning "CUDA not found. Installing CUDA 12.1..."
    
    # Download and install CUDA
    wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
    sudo sh cuda_12.1.0_530.30.02_linux.run --silent --toolkit
    
    # Add CUDA to PATH
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
    source ~/.bashrc
    
    rm cuda_12.1.0_530.30.02_linux.run
    print_success "CUDA installed"
fi

# Install uv for fast Python package management
print_status "Installing uv package manager..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    print_success "uv installed"
else
    print_success "uv already installed"
fi

# Make sure uv is in PATH for this session
export PATH="$HOME/.cargo/bin:$PATH"

# Create virtual environments
print_status "Creating virtual environments..."

# Backend environment
cd "$PROJECT_DIR/backend"
if [ ! -d ".venv" ]; then
    python3.10 -m venv .venv
    print_success "Backend virtual environment created"
else
    print_success "Backend virtual environment already exists"
fi

# Frontend environment
cd "$PROJECT_DIR/frontend"
if [ ! -d ".venv" ]; then
    python3.10 -m venv .venv
    print_success "Frontend virtual environment created"
else
    print_success "Frontend virtual environment already exists"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."

# Backend dependencies
cd "$PROJECT_DIR/backend"
source .venv/bin/activate
pip install --upgrade pip
pip install uv
uv pip install -e .
deactivate
print_success "Backend dependencies installed"

# Frontend dependencies
cd "$PROJECT_DIR/frontend"
source .venv/bin/activate
pip install --upgrade pip
pip install uv
uv pip install -r requirements.txt
deactivate
print_success "Frontend dependencies installed"

# Create necessary directories
print_status "Creating output directories..."
mkdir -p "$PROJECT_DIR/output/models"
mkdir -p "$PROJECT_DIR/output/logs"
mkdir -p "$PROJECT_DIR/output/temp"
mkdir -p "$PROJECT_DIR/cache"
mkdir -p "$PROJECT_DIR/models"
print_success "Directories created"

# Create .env file if it doesn't exist
cd "$PROJECT_DIR"
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    
    print_warning "⚠️  IMPORTANT: Please edit .env file with your HuggingFace token:"
    echo "nano .env"
    echo ""
    echo "Required settings:"
    echo "- HF_TOKEN: Your HuggingFace token from https://huggingface.co/settings/tokens"
    echo "- CUDA_VISIBLE_DEVICES: GPU devices to use (e.g., '0,1,2,3')"
    echo "- GPU_MEMORY_FRACTION: Memory fraction per GPU (e.g., 0.8)"
else
    print_success ".env file already exists"
fi

# Set up systemd services
print_status "Setting up systemd services..."

# Create systemd service files
sudo tee /etc/systemd/system/step1x3d-backend.service > /dev/null <<EOF
[Unit]
Description=Step1X-3D Backend Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/backend/.venv/bin:/usr/local/cuda/bin:/usr/bin:/bin
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/backend/.venv/bin/python $PROJECT_DIR/backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/step1x3d-frontend.service > /dev/null <<EOF
[Unit]
Description=Step1X-3D Frontend Service
After=network.target step1x3d-backend.service
Requires=step1x3d-backend.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR/frontend
Environment=PATH=$PROJECT_DIR/frontend/.venv/bin:/usr/bin:/bin
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/frontend/.venv/bin/streamlit run $PROJECT_DIR/frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable step1x3d-backend.service
sudo systemctl enable step1x3d-frontend.service

print_success "Systemd services configured"

# Configure firewall
print_status "Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 8000/tcp  # Backend
    sudo ufw allow 8501/tcp  # Frontend
    print_success "Firewall configured"
else
    print_warning "UFW not found, please configure firewall manually"
fi

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Final setup instructions
print_success "🎉 Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Configure your HuggingFace token:"
echo "   nano .env"
echo "   # Add: HF_TOKEN=hf_your_token_here"
echo ""
echo "2. Start the services:"
echo "   ./scripts/start.sh"
echo ""
echo "3. Check status:"
echo "   ./scripts/status.sh"
echo ""
echo "4. View logs:"
echo "   ./scripts/logs.sh"
echo ""
echo "5. Access the application:"
echo "   Frontend: http://$SERVER_IP:8501"
echo "   Backend:  http://$SERVER_IP:8000"
echo "   API Docs: http://$SERVER_IP:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For development mode:"
echo "   Backend: cd backend && source .venv/bin/activate && python main.py"
echo "   Frontend: cd frontend && source .venv/bin/activate && streamlit run app.py"
echo ""
