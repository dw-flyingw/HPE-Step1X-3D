# Self-Host Step1X-3D with Gradio

## Why Gradio?

✅ **Much simpler than FastAPI** for ML inference
✅ **Auto-generates UI** - no frontend coding needed
✅ **Built for ML models** - handles file uploads, progress bars automatically
✅ **What HF Spaces use** - battle-tested for ML deployment
✅ **Less code** - ~150 lines vs 750+ lines

## Quick Start

### On Your Remote Server

```bash
# 1. Transfer files
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/

# 2. SSH to server
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D

# 3. Deploy
chmod +x deploy-gradio.sh
./deploy-gradio.sh
```

That's it! The UI will be available at `http://your-server:7860`

## What You Get

### Web UI with Two Tabs:

1. **Geometry Only (Fast)**
   - Upload image
   - Adjust settings (guidance scale, inference steps, seed)
   - Download untextured .glb file
   - ~30-60 seconds per generation

2. **With Texture (Slow)**
   - Upload image
   - Adjust settings
   - Download textured .glb file
   - ~2-5 minutes per generation

### Features:
- ✅ Drag & drop image upload
- ✅ Real-time progress updates
- ✅ Adjustable parameters via sliders
- ✅ Direct file download
- ✅ Clean, intuitive interface
- ✅ No coding needed to use it

## Manual Setup

If the script doesn't work:

```bash
cd ~/HPE-Step1X-3D

# Build
docker compose build gradio

# Start
docker compose up -d gradio

# Check logs
docker compose logs -f gradio

# Stop
docker compose down
```

## Access the UI

**Locally:**
```
http://localhost:7860
```

**From another machine:**
```
http://your-server-ip:7860
```

**Make it public (temporarily):**
In `app_gradio.py`, change:
```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True  # ← Add this for public link
)
```

## Configuration

Edit `.env` file:
```bash
GRADIO_PORT=7860
OUTPUT_DIR=/app/output
```

## Firewall Setup

If you need to access from other machines:

```bash
# Ubuntu/Debian
sudo ufw allow 7860/tcp

# RHEL/CentOS
sudo firewall-cmd --permanent --add-port=7860/tcp
sudo firewall-cmd --reload
```

## API Access (Optional)

Gradio also provides an API:

```python
from gradio_client import Client

client = Client("http://your-server:7860")
result = client.predict(
    image="path/to/image.png",
    guidance_scale=7.5,
    num_steps=50,
    seed=2025,
    api_name="/generate_geometry"
)
```

## Advantages Over FastAPI Backend

| Feature | Gradio | FastAPI (old) |
|---------|--------|---------------|
| Lines of Code | ~150 | 750+ |
| UI Included | ✅ Auto-generated | ❌ Need separate frontend |
| Setup Time | 5 minutes | Hours of debugging |
| File Uploads | ✅ Built-in | ❌ Manual handling |
| Progress Bar | ✅ Automatic | ❌ Manual implementation |
| Error Display | ✅ User-friendly | ❌ Need custom error pages |
| Dependency Issues | ✅ Minimal | ❌ Many (data loaders, training, etc.) |
| API Available | ✅ Auto-generated | ✅ Manual |
| Queue System | ✅ Built-in | ❌ Manual |
| Share Option | ✅ One flag | ❌ Complex setup |

## Troubleshooting

### Port already in use
```bash
# Check what's using port 7860
sudo lsof -i :7860

# Use different port
echo "GRADIO_PORT=7861" >> .env
docker compose up -d gradio
```

### Can't access from browser
```bash
# Check if container is running
docker compose ps

# Check firewall
sudo ufw status

# Check logs
docker compose logs gradio
```

### Models not loading
```bash
# Check GPU
docker exec gradio-1 nvidia-smi

# Check space
df -h

# Check logs for download progress
docker compose logs -f gradio
```

## Resource Requirements

- **GPU**: 8GB+ VRAM recommended (16GB for texture)
- **RAM**: 16GB+ recommended
- **Disk**: 20GB+ free space
- **Network**: Good internet for first run (model downloads)

## Performance

**First run (cold start):**
- Model download: 10-20 minutes
- Model loading: 2-5 minutes
- First generation: 1-2 minutes

**Subsequent runs (warm):**
- Geometry only: 30-60 seconds
- With texture: 2-5 minutes

## Scaling

For production with multiple users:

```python
# In app_gradio.py, add:
demo.queue(max_size=10)  # Queue up to 10 requests
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    max_threads=4  # Handle 4 concurrent requests
)
```

## Comparison with HF Space

| Feature | Self-Hosted Gradio | HF Space |
|---------|-------------------|----------|
| Cost | GPU server cost | Free (slow) or paid |
| Speed | Fast (dedicated GPU) | Slow (shared) |
| Privacy | ✅ Private | ⚠️ Public |
| Customization | ✅ Full control | ⚠️ Limited |
| Maintenance | ⚠️ You manage | ✅ HF manages |

## Next Steps

1. ✅ Deploy with `./deploy-gradio.sh`
2. ✅ Access UI at `http://your-server:7860`
3. ✅ Upload test image
4. ✅ Generate 3D model
5. ✅ Download and view result

Done! No frontend coding needed, no complex API, just a simple web UI. 🎉

