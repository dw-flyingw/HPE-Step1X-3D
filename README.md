# Step1X-3D Generator v2.0

A modern, production-ready system for generating 3D models from images and text using local GPU inference with Step1X-3D and Stable Diffusion XL.

## 🚀 Features

- **Local GPU Inference**: Runs entirely on your hardware with 4x Nvidia L40 GPUs
- **Image to 3D**: Upload images and generate 3D models
- **Text to 3D**: Generate images from text, then create 3D models
- **3D Model Processing**: Convert and modify existing 3D models (.glb, .obj, .nii.gz)
- **Medical Imaging**: Support for NIfTI medical imaging files
- **Modern Architecture**: FastAPI backend + Streamlit frontend
- **GPU Management**: Intelligent GPU resource allocation and monitoring
- **Production Ready**: Systemd services, logging, error handling

## 📁 Project Structure

```
HPE-Step1X-3D/
├── frontend/                 # Streamlit UI
│   ├── app.py               # Main frontend application
│   └── requirements.txt     # Frontend dependencies
├── backend/                 # FastAPI server
│   ├── app/                 # Application code
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic (GPU, Model, Mesh)
│   │   ├── routes/         # API endpoints
│   │   └── config.py       # Configuration management
│   ├── main.py             # FastAPI application
│   └── pyproject.toml      # Backend dependencies
├── output/                  # Generated files
│   ├── models/             # Generated 3D models
│   ├── logs/               # Application logs
│   └── temp/               # Temporary files
├── scripts/                 # Management scripts (run on Ubuntu server)
│   ├── install.sh          # First-time installation
│   ├── update.sh           # Update after git pull
│   ├── start.sh            # Start services
│   ├── stop.sh             # Stop services
│   ├── status.sh           # Check service status
│   └── logs.sh             # View logs
├── docs/                    # Documentation
│   └── DEPLOYMENT.md       # Detailed deployment guide
├── env.example              # Environment template
├── QUICK_START.md          # Quick start guide
└── README.md               # This file
```

## 🎯 Quick Start

### On Ubuntu Server (First Time)

```bash
# 1. Clone repository
git clone <your-github-repo> ~/HPE-Step1X-3D
cd ~/HPE-Step1X-3D

# 2. Run installation
chmod +x scripts/*.sh
./scripts/install.sh

# 3. Configure environment
nano .env
# Add: HF_TOKEN=hf_your_token_here

# 4. Start services
./scripts/start.sh

# 5. Check status
./scripts/status.sh
```

**Access**: http://your-server:8501

See **[QUICK_START.md](QUICK_START.md)** for detailed workflow.

## 🔄 Development Workflow

### Git-Based Workflow

This project uses a Git-based development workflow:

**On MacBook (Development):**
```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main
```

**On Ubuntu Server (Deployment):**
```bash
# Pull changes
git pull origin main

# Update and restart
./scripts/update.sh
```

## 🛠️ Management Commands

All scripts run **on the Ubuntu server**:

```bash
./scripts/install.sh    # First-time setup (installs everything)
./scripts/update.sh     # Update after git pull
./scripts/start.sh      # Start services
./scripts/stop.sh       # Stop services
./scripts/status.sh     # Check service status
./scripts/logs.sh       # View logs
```

## 📡 API Endpoints

### Generation
- `POST /api/v1/text-to-image` - Generate image from text
- `POST /api/v1/generate-3d` - Generate 3D model from image
- `POST /api/v1/convert-mesh` - Convert 3D model format
- `GET /api/v1/files` - List generated files
- `GET /api/v1/download/{filename}` - Download file

### System
- `GET /health/` - System health check
- `GET /health/models` - Model status
- `GET /health/gpu` - GPU information
- `POST /health/models/load` - Load models
- `POST /health/gpu/clear-cache` - Clear GPU cache

## 🎮 GPU Management

The system intelligently manages your 4x Nvidia L40 GPUs:

- **Automatic GPU Selection**: Uses available GPUs from CUDA_VISIBLE_DEVICES
- **Memory Management**: Configurable memory fraction per GPU
- **Load Balancing**: Distributes requests across available GPUs
- **Monitoring**: Real-time GPU usage and memory tracking
- **Cache Management**: Automatic GPU memory cleanup

Configure in `.env`:
```bash
CUDA_VISIBLE_DEVICES=0,1,2,3
GPU_MEMORY_FRACTION=0.8
MAX_CONCURRENT_REQUESTS=4
```

## 📊 Supported Formats

### Input Formats
- **Images**: PNG, JPG, JPEG
- **3D Models**: GLB, OBJ
- **Medical**: NIfTI (.nii.gz)

### Output Formats
- **3D Models**: GLB, OBJ, STL, PLY
- **Images**: PNG, JPG

## ⚙️ Configuration

Key environment variables in `.env`:

```bash
# Required
HF_TOKEN=hf_your_token_here                    # From https://huggingface.co/settings/tokens

# GPU Configuration
CUDA_VISIBLE_DEVICES=0,1,2,3                   # GPUs to use
GPU_MEMORY_FRACTION=0.8                         # Memory per GPU (0.0-1.0)
MAX_CONCURRENT_REQUESTS=4                       # Concurrent generations

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# Model Configuration
STEP1X3D_MODEL_ID=stepfun-ai/Step1X-3D
SDXL_MODEL_ID=stabilityai/stable-diffusion-xl-base-1.0
MODEL_CACHE_DIR=./models

# Logging
LOG_LEVEL=INFO                                  # DEBUG, INFO, WARNING, ERROR
DEBUG=False
```

## 🐛 Troubleshooting

### Quick Diagnostics

```bash
# Check service status
./scripts/status.sh

# View logs
./scripts/logs.sh

# Check GPU
nvidia-smi

# Test backend
curl http://localhost:8000/health/

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

### Common Issues

**Services Won't Start:**
```bash
./scripts/logs.sh           # Check logs
cat .env                    # Verify configuration
./scripts/install.sh        # Reinstall if needed
```

**GPU Not Detected:**
```bash
nvidia-smi                  # Check GPU status
nvcc --version              # Check CUDA
sudo apt install nvidia-driver-535
```

**Models Not Loading:**
```bash
cat .env | grep HF_TOKEN    # Verify token
curl -X POST http://localhost:8000/health/models/load
./scripts/stop.sh && ./scripts/start.sh
```

**Out of Memory:**
```bash
# Edit .env: GPU_MEMORY_FRACTION=0.6
curl -X POST http://localhost:8000/health/gpu/clear-cache
./scripts/stop.sh && ./scripts/start.sh
```

## 📈 Performance

- **Async Processing**: Non-blocking I/O operations
- **GPU Acceleration**: CUDA-optimized inference
- **Memory Efficient**: Intelligent memory management
- **Concurrent Requests**: Multiple simultaneous generations
- **Caching**: Model and result caching

### Performance Tuning

For 4x L40 GPUs (48GB each):

```bash
# Conservative (stable)
GPU_MEMORY_FRACTION=0.7
MAX_CONCURRENT_REQUESTS=2

# Aggressive (maximum throughput)
GPU_MEMORY_FRACTION=0.9
MAX_CONCURRENT_REQUESTS=4
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide with workflow
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Detailed deployment guide
- **API Documentation** - http://your-server:8000/docs (interactive)
- **Health Check** - http://your-server:8000/health/

## 🔐 Security

- Input validation and sanitization
- File type verification
- Path traversal protection
- CORS configuration
- Error handling without information leakage

### Firewall Setup

```bash
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 8501/tcp  # Frontend UI
sudo ufw enable
```

## 🔄 Updates

### Update Code from GitHub

```bash
# On Ubuntu server
cd ~/HPE-Step1X-3D
git pull origin main
./scripts/update.sh
```

### Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install --reinstall nvidia-driver-535
sudo reboot  # if needed
```

## 📝 Logs

### View Logs

```bash
# Application logs
./scripts/logs.sh

# Backend only
./scripts/logs.sh backend

# Frontend only
./scripts/logs.sh frontend

# System logs
sudo journalctl -u step1x3d-backend.service -f
```

### Log Files

```bash
# Application logs
tail -f output/logs/backend.log

# System service logs
sudo journalctl -u step1x3d-backend.service --no-pager
```

## 🎓 Usage Examples

### Generate 3D from Image

```bash
curl -X POST http://localhost:8000/api/v1/generate-3d \
  -F "image=@input.jpg" \
  -F "mode=geometry" \
  -F "guidance_scale=7.5" \
  -F "num_steps=50" \
  -F "seed=2025"
```

### Generate Image from Text

```bash
curl -X POST http://localhost:8000/api/v1/text-to-image \
  -F "prompt=a red sports car" \
  -F "width=1024" \
  -F "height=1024"
```

### Convert 3D Model

```bash
curl -X POST http://localhost:8000/api/v1/convert-mesh \
  -F "file=@model.obj" \
  -F "target_format=glb"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support:
1. Check [QUICK_START.md](QUICK_START.md) for workflow
2. Check [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for troubleshooting
3. Run `./scripts/status.sh` to check system status
4. View logs with `./scripts/logs.sh`
5. Open an issue on GitHub

## 🎯 System Requirements

### Hardware
- Ubuntu 20.04+ server
- 4x Nvidia L40 GPUs (or compatible)
- 32GB+ RAM
- 100GB+ storage

### Software
- NVIDIA drivers 535+
- CUDA 12.1+
- Python 3.10+
- Git

## 🌟 Features by Tab

### 🚀 Generate from Image
- Upload images to create 3D models
- Choose geometry (fast) or textured (detailed)
- Configurable inference steps and guidance

### ✍️ Generate from Prompt
- Text → Image → 3D pipeline
- Powered by Stable Diffusion XL
- Full control over generation parameters

### 🔄 Modify 3D Model
- Upload existing 3D models
- Convert between formats
- Apply modifications with text prompts

### 📂 View 3D Models
- Browse generated models
- Download in multiple formats
- View mesh statistics

### 📊 System Monitor
- Real-time GPU monitoring
- Model status tracking
- System resource usage

---

**Built with ❤️ for high-performance 3D model generation**

For quick start, see **[QUICK_START.md](QUICK_START.md)**