# Native Setup Guide (No Docker)

Run Step1X-3D directly on your server without Docker containers.

## Prerequisites

On your remote server:
- ✅ Python 3.10 or 3.11
- ✅ NVIDIA GPU with CUDA drivers
- ✅ 20GB+ free disk space
- ✅ Internet connection (for downloads)

## Quick Start

### 1. Transfer Files to Remote Server

```bash
# From your local machine
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/
```

### 2. SSH to Server and Setup

```bash
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D

# One-time setup (10-15 minutes)
chmod +x setup-native.sh
./setup-native.sh
```

This will:
- Create Python virtual environment
- Install PyTorch with CUDA support
- Install all dependencies
- Clone Step1X-3D repository

### 3. Start Backend (Gradio)

```bash
# Option A: Run in foreground (see logs)
./run-gradio.sh

# Option B: Run in background
./run-gradio-background.sh
```

Access backend at: `http://your-server:7860`

### 4. Start Frontend (Optional)

In another terminal:

```bash
cd ~/HPE-Step1X-3D
./run-frontend.sh
```

Access frontend at: `http://your-server:8501`

## Services

### Backend (Gradio) - Port 7860

**Full-featured UI with:**
- Image upload
- Parameter controls
- Direct 3D model download
- Two generation modes (geometry/textured)

**Start:**
```bash
./run-gradio.sh              # Foreground
./run-gradio-background.sh   # Background
```

**Stop:**
```bash
Ctrl+C                       # If foreground
./stop-gradio.sh            # If background
```

**Logs:**
```bash
tail -f logs/gradio.log     # If background
```

### Frontend (Streamlit) - Port 8501

**Simple interface that:**
- Connects to Gradio backend
- Provides alternative UI
- Optional (Gradio UI is self-sufficient)

**Start:**
```bash
./run-frontend.sh
```

## Advantages of Native Setup

✅ **Faster iteration** - No Docker rebuild
✅ **Easier debugging** - Direct Python access
✅ **Better performance** - No container overhead
✅ **Simpler logs** - Direct stdout/stderr
✅ **Quick updates** - Just edit and restart

## Common Commands

```bash
# Start backend
./run-gradio.sh

# Start in background
./run-gradio-background.sh

# View logs
tail -f logs/gradio.log

# Stop background service
./stop-gradio.sh

# Restart
./stop-gradio.sh && ./run-gradio-background.sh

# Check if running
ps aux | grep app_gradio
```

## Firewall Setup

If accessing from another machine:

```bash
# Backend port
sudo ufw allow 7860/tcp

# Frontend port (if using)
sudo ufw allow 8501/tcp
```

## Environment Variables

Create `.env` file (optional):

```bash
# Backend
GRADIO_PORT=7860

# Frontend
STREAMLIT_PORT=8501
BACKEND_URL=http://localhost:7860
```

## Troubleshooting

### "No module named 'torch'"

```bash
source venv/bin/activate
./setup-native.sh
```

### "CUDA out of memory"

- Close other GPU processes: `nvidia-smi`
- Reduce batch size in code
- Use geometry-only mode (less memory)

### Port already in use

```bash
# Find what's using the port
sudo lsof -i :7860

# Kill it
kill -9 <PID>
```

### Models not loading

```bash
# Check internet connection
ping huggingface.co

# Check disk space
df -h

# Check logs
tail -f logs/gradio.log
```

## Performance

**First run:**
- Setup: 10-15 minutes
- Model download: 5-10 minutes
- Model loading: 2-5 minutes

**Subsequent runs:**
- Startup: 2-5 minutes (model loading)
- Generation: 30-60 sec (geometry) or 2-5 min (textured)

## Updating

```bash
# Update Step1X-3D code
cd Step1X-3D
git pull

# Update dependencies
source venv/bin/activate
pip install --upgrade gradio transformers diffusers

# Restart services
./stop-gradio.sh
./run-gradio-background.sh
```

## Running as System Service (Optional)

Create systemd service:

```bash
sudo tee /etc/systemd/system/step1x3d.service << EOF
[Unit]
Description=Step1X-3D Gradio Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/run-gradio.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable step1x3d
sudo systemctl start step1x3d

# Check status
sudo systemctl status step1x3d

# View logs
sudo journalctl -u step1x3d -f
```

## Directory Structure

```
HPE-Step1X-3D/
├── venv/                    # Python virtual environment
├── Step1X-3D/              # Cloned repository
├── backend/
│   ├── app_gradio.py       # Gradio backend
│   └── requirements_gradio.txt
├── frontend/
│   └── app_streamlit.py    # Streamlit frontend
├── output/                  # Generated 3D models
├── logs/                    # Log files
│   ├── gradio.log
│   └── gradio.pid
├── setup-native.sh          # One-time setup
├── run-gradio.sh           # Start backend (foreground)
├── run-gradio-background.sh # Start backend (background)
├── stop-gradio.sh          # Stop backend
└── run-frontend.sh         # Start frontend
```

## Comparison: Docker vs Native

| Feature | Docker | Native |
|---------|--------|--------|
| Setup Time | Slow (build) | Fast (pip install) |
| Restart | Slow | Fast |
| Debugging | Harder | Easier |
| Updates | Rebuild | Just restart |
| Isolation | ✅ Isolated | ⚠️ System-wide |
| Portability | ✅ Portable | ⚠️ Server-specific |
| Performance | Good | Better |

## Recommended Workflow

**Development:**
1. Use native setup
2. Iterate quickly
3. Test changes immediately

**Production:**
1. Finalize code
2. Build Docker image
3. Deploy with Docker Compose

## Next Steps

1. ✅ Run `./setup-native.sh` (one time)
2. ✅ Run `./run-gradio.sh` (or background version)
3. ✅ Open `http://your-server:7860` in browser
4. ✅ Upload image and generate 3D model

Done! No Docker, no containers, just Python! 🐍

