# Setup Guide

## Overview

This is a **clean, simple** Step1X-3D inference system:
- **Backend**: FastAPI (port 8000) wraps HuggingFace Inference API
- **Frontend**: Streamlit UI (port 8501) for image upload
- **Dependencies**: Managed by `uv` (fast, reliable)
- **No local models**: Uses HuggingFace's managed inference

## Prerequisites

1. **HuggingFace Account**: https://huggingface.co/join
2. **HuggingFace Token**: Get from https://huggingface.co/settings/tokens
   - Create a token with "Read" access
3. **Ubuntu Server**: With Python 3.10+

## Installation (One Time)

### On Your Remote Server

```bash
# Navigate to project
cd ~/HPE-Step1X-3D

# Run setup (installs everything with uv)
chmod +x setup.sh
./setup.sh
```

This will:
- Install `uv` if not present
- Create virtual environments for backend and frontend
- Install all dependencies
- Create output and logs directories
- Create .env from template

### Configure HuggingFace Token

```bash
# Edit .env file
nano .env

# Add your actual HF token:
HF_TOKEN=hf_your_actual_token_here
```

Save and exit (Ctrl+X, Y, Enter)

## Usage

### Start Services

```bash
./start.sh
```

Both backend and frontend will start in the background.

### Access the UI

Open in your browser:
- `http://your-server-ip:8501`

### Use the Application

1. Upload an image
2. Choose mode (geometry or textured)
3. Adjust settings (optional)
4. Click "Generate 3D Model"
5. Wait 30-60 seconds
6. Download the .glb file

### Stop Services

```bash
./stop.sh
```

### Check Status

```bash
./status.sh
```

### View Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs  
tail -f logs/frontend.log

# Both
tail -f logs/*.log
```

## Ports

- **Frontend (Streamlit)**: 8501
- **Backend (FastAPI)**: 8000

### Change Ports

Edit `.env` file:
```bash
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

Then restart: `./stop.sh && ./start.sh`

## Firewall Setup

If accessing from another machine:

```bash
# Allow Streamlit port
sudo ufw allow 8501/tcp

# Allow backend port (if needed for direct API access)
sudo ufw allow 8000/tcp
```

## How It Works

1. **You upload image** in Streamlit UI (port 8501)
2. **Frontend sends to backend** (FastAPI on port 8000)
3. **Backend calls HuggingFace** Inference API
4. **HuggingFace processes** on their GPU
5. **3D model returned** through backend to frontend
6. **You download** the .glb file

## No Local GPU Needed

The actual model runs on HuggingFace's servers, so:
- ✅ No local CUDA setup
- ✅ No PyTorch installation
- ✅ No model downloading
- ✅ Minimal dependencies
- ✅ Fast setup

## Cost

HuggingFace Inference API (free tier):
- Generous free quota per month
- Rate limits apply
- Perfect for development/testing

For production, consider HF Pro or Inference Endpoints.

## Troubleshooting

### "Module not found" errors
```bash
cd backend
source .venv/bin/activate
uv pip install -e .
```

### Backend returns 401
- Check HF_TOKEN in .env
- Verify token is valid: https://huggingface.co/settings/tokens

### Backend returns 503
- Model is loading (first request)
- Wait 30-60 seconds and retry

### Frontend can't connect to backend
```bash
# Check backend is running
./status.sh

# Check logs
tail -f logs/backend.log

# Verify BACKEND_URL in .env
cat .env
```

### Services won't start
```bash
# Check if ports are in use
sudo lsof -i :8000
sudo lsof -i :8501

# Check logs for errors
cat logs/backend.log
cat logs/frontend.log
```

## Development

### Run in Foreground (See Logs)

```bash
# Backend
cd backend
source .venv/bin/activate
python3 main.py

# Frontend (in another terminal)
cd frontend
source .venv/bin/activate
streamlit run app.py --server.port 8501
```

### Update Dependencies

```bash
# Backend
cd backend
source .venv/bin/activate
uv pip install package-name

# Frontend
cd frontend
source .venv/bin/activate
uv pip install package-name
```

## Project Structure

```
HPE-Step1X-3D/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── pyproject.toml       # Dependencies
│   └── .venv/              # Virtual environment (created by setup)
├── frontend/
│   ├── app.py              # Streamlit app
│   ├── pyproject.toml      # Dependencies
│   └── .venv/              # Virtual environment (created by setup)
├── output/                  # Generated 3D models
├── logs/                    # Service logs
│   ├── backend.log
│   ├── frontend.log
│   ├── backend.pid
│   └── frontend.pid
├── .env                     # Configuration (you create this)
├── env.template             # Template for .env
├── setup.sh                 # One-time setup
├── start.sh                 # Start services
├── stop.sh                  # Stop services
└── status.sh                # Check status
```

## Next Steps

After setup:
1. Get your HF token
2. Edit .env
3. Run `./start.sh`
4. Open http://your-server:8501
5. Generate 3D models!

Simple and clean! 🎉

