# Deployment Guide

## Overview

This guide covers deploying the Step1X-3D system to your Ubuntu server with 4x Nvidia L40 GPUs.

## Prerequisites

### Hardware Requirements
- Ubuntu 20.04+ server
- 4x Nvidia L40 GPUs (or compatible)
- 32GB+ RAM
- 100GB+ storage
- Stable internet connection

### Software Requirements
- NVIDIA drivers (535+)
- CUDA 12.1+
- Python 3.10+
- HuggingFace account

## Quick Deployment

### 1. One-Command Setup

```bash
# From your local machine
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/

# On remote server
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Edit environment file
nano .env

# Add your HuggingFace token
HF_TOKEN=hf_your_actual_token_here

# Configure GPU settings
CUDA_VISIBLE_DEVICES=0,1,2,3
GPU_MEMORY_FRACTION=0.8
```

### 3. Start Services

```bash
# Start all services
./scripts/start.sh

# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh
```

## Manual Setup

### 1. System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.10 python3.10-venv python3-pip \
    git curl wget build-essential cmake \
    libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libgtk-3-dev libatlas-base-dev gfortran \
    libhdf5-dev libopenblas-dev liblapack-dev
```

### 2. NVIDIA Setup

```bash
# Install NVIDIA drivers
sudo apt install nvidia-driver-535

# Install CUDA 12.1
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run --silent --toolkit

# Add to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 3. Python Environment

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Create virtual environments
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
uv pip install -e .

cd ../frontend
python3.10 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 4. Systemd Services

```bash
# Create service files (done automatically by setup.sh)
sudo systemctl daemon-reload
sudo systemctl enable step1x3d-backend.service
sudo systemctl enable step1x3d-frontend.service
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Required
HF_TOKEN=hf_your_token_here

# GPU Configuration
CUDA_VISIBLE_DEVICES=0,1,2,3
GPU_MEMORY_FRACTION=0.8
MAX_CONCURRENT_REQUESTS=4

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# Model Configuration
STEP1X3D_MODEL_ID=stepfun-ai/Step1X-3D
SDXL_MODEL_ID=stabilityai/stable-diffusion-xl-base-1.0

# Development
DEBUG=False
RELOAD=False
LOG_LEVEL=INFO
```

### GPU Memory Management

For 4x L40 GPUs (48GB each):

```bash
# Conservative settings
GPU_MEMORY_FRACTION=0.7
MAX_CONCURRENT_REQUESTS=2

# Aggressive settings
GPU_MEMORY_FRACTION=0.9
MAX_CONCURRENT_REQUESTS=4
```

## Service Management

### Using Scripts

```bash
# Start services
./scripts/start.sh

# Stop services
./scripts/stop.sh

# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh
```

### Using Systemd

```bash
# Start services
sudo systemctl start step1x3d-backend.service
sudo systemctl start step1x3d-frontend.service

# Stop services
sudo systemctl stop step1x3d-frontend.service
sudo systemctl stop step1x3d-backend.service

# Check status
sudo systemctl status step1x3d-backend.service
sudo systemctl status step1x3d-frontend.service

# View logs
sudo journalctl -u step1x3d-backend.service -f
sudo journalctl -u step1x3d-frontend.service -f
```

## Monitoring

### System Monitoring

```bash
# GPU usage
watch -n 1 nvidia-smi

# System resources
htop

# Disk usage
df -h
du -sh output/
```

### Application Monitoring

```bash
# Health check
curl http://localhost:8000/health/

# Model status
curl http://localhost:8000/health/models

# GPU status
curl http://localhost:8000/health/gpu
```

### Log Monitoring

```bash
# Application logs
tail -f output/logs/backend.log

# System logs
sudo journalctl -u step1x3d-backend.service -f

# Error logs
sudo journalctl -u step1x3d-backend.service --priority=err
```

## Troubleshooting

### Common Issues

#### 1. GPU Not Detected

```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA
nvcc --version

# Reinstall if needed
sudo apt install --reinstall nvidia-driver-535
```

#### 2. Models Not Loading

```bash
# Check HuggingFace token
cat .env | grep HF_TOKEN

# Test token
python3 -c "from huggingface_hub import HfApi; api = HfApi(); print('Token valid')"

# Manual model load
curl -X POST http://localhost:8000/health/models/load
```

#### 3. Out of Memory

```bash
# Clear GPU cache
curl -X POST http://localhost:8000/health/gpu/clear-cache

# Reduce memory fraction
# Edit .env: GPU_MEMORY_FRACTION=0.6

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

#### 4. Services Won't Start

```bash
# Check service status
sudo systemctl status step1x3d-backend.service

# Check logs
sudo journalctl -u step1x3d-backend.service --no-pager

# Check ports
sudo lsof -i :8000
sudo lsof -i :8501
```

### Performance Tuning

#### GPU Optimization

```bash
# Increase GPU memory fraction
GPU_MEMORY_FRACTION=0.9

# Enable mixed precision
# Add to model service configuration

# Optimize batch sizes
MAX_CONCURRENT_REQUESTS=2
```

#### System Optimization

```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize swap
sudo swapon --show
```

## Security

### Firewall Configuration

```bash
# Allow required ports
sudo ufw allow 8000/tcp  # Backend
sudo ufw allow 8501/tcp  # Frontend

# Enable firewall
sudo ufw enable
```

### Access Control

```bash
# Restrict backend access
# Edit .env: BACKEND_HOST=127.0.0.1

# Use reverse proxy
# Configure nginx for external access
```

## Backup and Recovery

### Backup

```bash
# Backup configuration
cp .env .env.backup

# Backup generated models
tar -czf models-backup-$(date +%Y%m%d).tar.gz output/models/

# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz output/logs/
```

### Recovery

```bash
# Restore configuration
cp .env.backup .env

# Restore models
tar -xzf models-backup-YYYYMMDD.tar.gz

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

## Updates

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
cd backend && source .venv/bin/activate && uv pip install -e .
cd frontend && source .venv/bin/activate && uv pip install -r requirements.txt

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

### System Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update NVIDIA drivers
sudo apt install nvidia-driver-535

# Reboot if needed
sudo reboot
```

## Scaling

### Horizontal Scaling

For multiple servers:

1. Deploy on multiple servers
2. Use load balancer (nginx/HAProxy)
3. Configure shared storage for models
4. Implement distributed GPU management

### Vertical Scaling

For more GPUs:

1. Update CUDA_VISIBLE_DEVICES
2. Increase MAX_CONCURRENT_REQUESTS
3. Adjust GPU_MEMORY_FRACTION
4. Monitor performance metrics

## Support

For deployment issues:

1. Check logs: `./scripts/logs.sh`
2. Verify configuration: `cat .env`
3. Test connectivity: `curl http://localhost:8000/health/`
4. Check GPU status: `nvidia-smi`

Contact support with:
- System specifications
- Error logs
- Configuration files
- Reproduction steps
