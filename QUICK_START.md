# Quick Start Guide

## Workflow Overview

This project uses a **Git-based workflow**:
1. **On MacBook**: Develop code, commit, push to GitHub
2. **On Ubuntu Server**: Pull from GitHub, run scripts

## First-Time Setup (Ubuntu Server)

### 1. Clone Repository

```bash
# SSH to your Ubuntu server
ssh hpadmin@sut73

# Clone the repository
cd ~
git clone <your-github-repo-url> HPE-Step1X-3D
cd HPE-Step1X-3D
```

### 2. Run Installation

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run installation (installs everything)
./scripts/install.sh
```

This will:
- Install system dependencies
- Install NVIDIA drivers and CUDA (if needed)
- Create Python virtual environments
- Install all Python dependencies
- Set up systemd services
- Configure firewall

### 3. Configure Environment

```bash
# Edit environment file
nano .env

# Add your HuggingFace token (required!)
HF_TOKEN=hf_your_token_here

# Configure GPU settings
CUDA_VISIBLE_DEVICES=0,1,2,3
GPU_MEMORY_FRACTION=0.8
```

Get your HuggingFace token from: https://huggingface.co/settings/tokens

### 4. Start Services

```bash
# Start both backend and frontend
./scripts/start.sh

# Check status
./scripts/status.sh
```

### 5. Access Application

Open in your browser:
- **Frontend**: http://your-server-ip:8501
- **Backend API**: http://your-server-ip:8000
- **API Docs**: http://your-server-ip:8000/docs

## Daily Workflow

### On MacBook (Development)

```bash
# Make changes to code
nano backend/app/services/model_service.py

# Test locally if needed
./scripts/dev.sh

# Commit and push to GitHub
git add .
git commit -m "Update model service"
git push origin main
```

### On Ubuntu Server (Deployment)

```bash
# SSH to server
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D

# Pull latest changes
git pull origin main

# Update dependencies (if needed)
./scripts/update.sh

# Or just restart services
./scripts/stop.sh
./scripts/start.sh
```

## Management Commands

All commands are run **on the Ubuntu server**:

```bash
# Start services
./scripts/start.sh

# Stop services
./scripts/stop.sh

# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh              # Show recent logs
./scripts/logs.sh backend      # Follow backend logs
./scripts/logs.sh frontend     # Follow frontend logs

# Update after git pull
./scripts/update.sh

# Full reinstall
./scripts/install.sh
```

## Common Tasks

### Update Code from GitHub

```bash
# On Ubuntu server
cd ~/HPE-Step1X-3D
git pull origin main
./scripts/update.sh
```

### View Real-Time Logs

```bash
# Backend logs
./scripts/logs.sh backend

# Frontend logs
./scripts/logs.sh frontend

# System logs
sudo journalctl -u step1x3d-backend.service -f
```

### Monitor GPU Usage

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# GPU status in service status
./scripts/status.sh
```

### Restart Services

```bash
# Quick restart
./scripts/stop.sh && ./scripts/start.sh

# Or using systemd
sudo systemctl restart step1x3d-backend.service
sudo systemctl restart step1x3d-frontend.service
```

### Check Service Status

```bash
# Detailed status
./scripts/status.sh

# Quick check
sudo systemctl status step1x3d-backend.service
sudo systemctl status step1x3d-frontend.service
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
./scripts/logs.sh

# Check if ports are in use
sudo lsof -i :8000
sudo lsof -i :8501

# Verify .env configuration
cat .env

# Reinstall
./scripts/install.sh
```

### GPU Not Detected

```bash
# Check GPU status
nvidia-smi

# Check CUDA
nvcc --version

# Reinstall drivers
sudo apt install --reinstall nvidia-driver-535
sudo reboot
```

### Models Not Loading

```bash
# Check HuggingFace token
cat .env | grep HF_TOKEN

# Clear GPU cache
curl -X POST http://localhost:8000/health/gpu/clear-cache

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

### Update Dependencies

```bash
# After git pull
./scripts/update.sh

# Or manually
cd backend && source .venv/bin/activate && uv pip install -e .
cd frontend && source .venv/bin/activate && uv pip install -r requirements.txt
```

## Environment Variables

Key settings in `.env`:

```bash
# Required
HF_TOKEN=hf_your_token_here

# GPU Configuration
CUDA_VISIBLE_DEVICES=0,1,2,3      # Which GPUs to use
GPU_MEMORY_FRACTION=0.8            # Memory per GPU (0.0-1.0)
MAX_CONCURRENT_REQUESTS=4          # Concurrent generations

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# Model Configuration
MODEL_CACHE_DIR=./models
STEP1X3D_MODEL_ID=stepfun-ai/Step1X-3D
SDXL_MODEL_ID=stabilityai/stable-diffusion-xl-base-1.0

# Logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
DEBUG=False
```

## File Locations

```
~/HPE-Step1X-3D/
├── .env                          # Your configuration
├── output/
│   ├── models/                   # Generated 3D models
│   ├── logs/                     # Application logs
│   └── temp/                     # Temporary files
├── models/                       # Downloaded model cache
├── cache/                        # HuggingFace cache
└── scripts/                      # Management scripts
```

## Getting Help

### Check System Status

```bash
./scripts/status.sh
```

### View Recent Logs

```bash
./scripts/logs.sh
```

### Test Backend

```bash
curl http://localhost:8000/health/
```

### Test Frontend

```bash
# Open in browser
http://your-server-ip:8501
```

## Next Steps

1. ✅ Install on Ubuntu server: `./scripts/install.sh`
2. ✅ Configure .env with HuggingFace token
3. ✅ Start services: `./scripts/start.sh`
4. ✅ Access frontend at http://your-server-ip:8501
5. ✅ Generate your first 3D model!

For detailed documentation, see:
- `README.md` - Complete documentation
- `docs/DEPLOYMENT.md` - Deployment guide
