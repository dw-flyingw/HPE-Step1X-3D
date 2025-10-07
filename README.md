# Step1X-3D Inference System

Simple FastAPI backend + Streamlit frontend for [Step1X-3D](https://huggingface.co/stepfun-ai/Step1X-3D) model inference using HuggingFace Inference API.

## Architecture

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│  Streamlit  │──────>│   FastAPI   │──────>│  HuggingFace    │
│  Frontend   │       │   Backend   │       │  Inference API  │
│  Port 8501  │<──────│  Port 8000  │<──────│  (Managed GPU)  │
└─────────────┘       └─────────────┘       └─────────────────┘
```

- **Frontend**: Streamlit UI for image upload and 3D download
- **Backend**: FastAPI wrapper for HF Inference API
- **Inference**: HuggingFace manages the actual model and GPU

## Quick Start

### Prerequisites
- Ubuntu server (tested on 22.04)
- Python 3.10+
- HuggingFace account and token

### Setup (One Time)

```bash
# Transfer files to server
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ user@server:~/HPE-Step1X-3D/

# SSH to server
ssh user@server
cd ~/HPE-Step1X-3D

# Run setup
chmod +x setup.sh
./setup.sh

# Configure your HF token
nano .env
# Add your HF_TOKEN
```

### Run

```bash
# Start both services
./start.sh

# Check status
./status.sh

# Stop services
./stop.sh
```

### Access

- **Frontend**: http://your-server:8501
- **Backend API**: http://your-server:8000

## Commands

```bash
./setup.sh   # One-time setup (installs deps with uv)
./start.sh   # Start backend + frontend
./stop.sh    # Stop all services
./status.sh  # Check if running
```

## Configuration

Edit `.env` file:

```bash
HF_TOKEN=hf_your_token_here
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000
FRONTEND_PORT=8501
```

## Features

- ✅ Image to 3D generation
- ✅ Two modes: Geometry only (fast) or Textured (detailed)
- ✅ Adjustable parameters (guidance scale, steps, seed)
- ✅ Direct .glb file download
- ✅ Clean UI with Streamlit
- ✅ No local GPU needed (uses HF Inference API)
- ✅ Minimal dependencies (uses uv)

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI backend
│   └── pyproject.toml    # Dependencies (uv)
├── frontend/
│   ├── app.py            # Streamlit frontend
│   └── pyproject.toml    # Dependencies (uv)
├── output/               # Generated 3D models
├── logs/                 # Service logs
├── .env                  # Configuration
├── setup.sh             # Setup script
├── start.sh             # Start services
├── stop.sh              # Stop services
└── status.sh            # Check status
```

## Requirements

- Python 3.10+
- HuggingFace account
- HuggingFace token with API access
- Internet connection

## Cost

Using HuggingFace Inference API:
- **Free tier**: Limited requests per month
- **Pro**: ~$0.60/hour when actively processing
- **Scales to zero**: No cost when idle

## Troubleshooting

**Backend won't start:**
```bash
tail -f logs/backend.log
```

**Frontend can't connect to backend:**
```bash
# Check backend is running
./status.sh

# Check BACKEND_URL in .env
cat .env
```

**503 Model Loading:**
- First request may take 30-60 seconds
- HF is loading the model
- Retry after waiting

**401 Unauthorized:**
- Check HF_TOKEN in .env
- Verify token at https://huggingface.co/settings/tokens

## Support

- Model: https://huggingface.co/stepfun-ai/Step1X-3D
- HF Inference API: https://huggingface.co/inference-api
- Get token: https://huggingface.co/settings/tokens

