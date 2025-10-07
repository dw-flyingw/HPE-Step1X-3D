# Quick Start Guide

## One-Time Setup (First Time Only)

```bash
# On remote server (Ubuntu)
cd ~/HPE-Step1X-3D

# Setup (10-15 minutes - downloads everything)
./setup-native.sh
```

## Start Services

```bash
# Start both backend and frontend
./start-all.sh
```

**Access:**
- Backend: `http://your-server-ip:7860` (Gradio UI - ready to use!)
- Frontend: `http://your-server-ip:8501` (Streamlit UI - optional)

## Stop Services

```bash
./stop-all.sh
```

## Check Status

```bash
./status.sh
```

## View Logs

```bash
# Backend logs
tail -f logs/gradio.log

# Frontend logs
tail -f logs/streamlit.log

# Both logs
tail -f logs/*.log
```

## Quick Commands Cheat Sheet

```bash
./setup-native.sh    # One-time setup
./start-all.sh       # Start both services
./stop-all.sh        # Stop both services
./status.sh          # Check if running
tail -f logs/*.log   # View logs
```

## First Run Timeline

1. **Setup**: 10-15 minutes (one time)
2. **Start services**: 2-5 minutes (model loading)
3. **Generate 3D**: 30-60 seconds (geometry) or 2-5 min (textured)

## Troubleshooting

### Services won't start
```bash
# Check if virtual environment exists
ls venv/

# If not, run setup
./setup-native.sh
```

### Port already in use
```bash
# Check what's using the ports
sudo lsof -i :7860
sudo lsof -i :8501

# Kill the process or use different ports
```

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Should show your GPU
```

### Can't access from browser
```bash
# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 7860/tcp
sudo ufw allow 8501/tcp
```

## Using the UI

1. Open `http://your-server-ip:7860` in browser
2. Upload an image
3. Adjust parameters (optional)
4. Click "Generate"
5. Wait 30-60 seconds
6. Download the .glb file

Done! 🎉

