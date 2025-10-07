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
│   │   ├── services/       # Business logic
│   │   ├── routes/         # API endpoints
│   │   └── utils/          # Utilities
│   ├── main.py             # FastAPI application
│   └── pyproject.toml      # Backend dependencies
├── output/                  # Generated files
│   ├── models/             # Generated 3D models
│   ├── logs/               # Application logs
│   └── temp/               # Temporary files
├── scripts/                 # Deployment & management
│   ├── setup.sh            # Ubuntu server setup
│   ├── deploy.sh           # Remote deployment
│   └── dev.sh              # Development mode
├── docs/                    # Documentation
└── env.example              # Environment template
```

## 🛠️ Quick Start

### Prerequisites

- Ubuntu 20.04+ server with 4x Nvidia L40 GPUs
- NVIDIA drivers and CUDA 12.1+
- Python 3.10+
- HuggingFace account and token

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd HPE-Step1X-3D

# Copy environment template
cp env.example .env

# Edit configuration
nano .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Required: HuggingFace token
HF_TOKEN=hf_your_token_here

# GPU configuration
CUDA_VISIBLE_DEVICES=0,1,2,3
GPU_MEMORY_FRACTION=0.8

# Server configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

### 3. Deploy to Server

```bash
# Run setup script (installs everything)
./scripts/setup.sh

# Start services
./scripts/start.sh

# Check status
./scripts/status.sh
```

### 4. Access Application

- **Frontend**: http://your-server:8501
- **Backend API**: http://your-server:8000
- **API Documentation**: http://your-server:8000/docs

## 🖥️ Development

### Local Development

```bash
# Start both services in development mode
./scripts/dev.sh

# Or start individually
./scripts/dev.sh backend    # Backend only
./scripts/dev.sh frontend   # Frontend only
```

### Development Features

- Hot reload enabled
- Debug logging
- Auto-restart on file changes
- Interactive debugging

## 📡 API Endpoints

### Generation
- `POST /api/v1/text-to-image` - Generate image from text
- `POST /api/v1/generate-3d` - Generate 3D model from image
- `POST /api/v1/convert-mesh` - Convert 3D model format

### Management
- `GET /health/` - System health check
- `GET /api/v1/files` - List generated files
- `GET /api/v1/download/{filename}` - Download file

### System
- `GET /health/models` - Model status
- `GET /health/gpu` - GPU information
- `POST /health/models/load` - Load models
- `POST /health/gpu/clear-cache` - Clear GPU cache

## 🔧 Management Commands

```bash
# Service management
./scripts/start.sh          # Start services
./scripts/stop.sh           # Stop services
./scripts/status.sh         # Check status
./scripts/logs.sh           # View logs

# Development
./scripts/dev.sh            # Development mode
./scripts/dev.sh backend    # Backend only
./scripts/dev.sh frontend   # Frontend only

# Deployment
./scripts/deploy.sh         # Deploy to remote server
./scripts/deploy.sh --setup-only  # Setup only
./scripts/deploy.sh --start-only  # Start services only
```

## 🎮 GPU Management

The system intelligently manages your 4x Nvidia L40 GPUs:

- **Automatic GPU Selection**: Uses available GPUs from CUDA_VISIBLE_DEVICES
- **Memory Management**: Configurable memory fraction per GPU
- **Load Balancing**: Distributes requests across available GPUs
- **Monitoring**: Real-time GPU usage and memory tracking
- **Cache Management**: Automatic GPU memory cleanup

## 📊 Supported Formats

### Input Formats
- **Images**: PNG, JPG, JPEG
- **3D Models**: GLB, OBJ
- **Medical**: NIfTI (.nii.gz)

### Output Formats
- **3D Models**: GLB, OBJ, STL, PLY
- **Images**: PNG, JPG

## 🔐 Security

- Input validation and sanitization
- File type verification
- Path traversal protection
- CORS configuration
- Error handling without information leakage

## 📈 Performance

- **Async Processing**: Non-blocking I/O operations
- **GPU Acceleration**: CUDA-optimized inference
- **Memory Efficient**: Intelligent memory management
- **Concurrent Requests**: Multiple simultaneous generations
- **Caching**: Model and result caching

## 🐛 Troubleshooting

### Common Issues

1. **GPU Not Detected**
   ```bash
   nvidia-smi  # Check GPU status
   ./scripts/setup.sh  # Reinstall drivers
   ```

2. **Models Not Loading**
   ```bash
   # Check HuggingFace token
   cat .env | grep HF_TOKEN
   
   # Manually load models
   curl -X POST http://localhost:8000/health/models/load
   ```

3. **Services Won't Start**
   ```bash
   ./scripts/status.sh  # Check service status
   ./scripts/logs.sh    # View error logs
   ```

4. **Memory Issues**
   ```bash
   # Clear GPU cache
   curl -X POST http://localhost:8000/health/gpu/clear-cache
   
   # Reduce memory fraction in .env
   GPU_MEMORY_FRACTION=0.6
   ```

### Logs

```bash
# Application logs
tail -f output/logs/backend.log

# System service logs
sudo journalctl -u step1x3d-backend.service -f
sudo journalctl -u step1x3d-frontend.service -f

# GPU monitoring
watch -n 1 nvidia-smi
```

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
cd backend && source .venv/bin/activate && uv pip install -e .
cd frontend && source .venv/bin/activate && uv pip install -r requirements.txt

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Health Check](http://localhost:8000/health/) - System status
- [GPU Monitor](http://localhost:8000/health/gpu) - GPU information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the logs
- Open an issue on GitHub

---

**Built with ❤️ for high-performance 3D model generation**
