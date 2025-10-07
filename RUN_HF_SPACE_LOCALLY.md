# Run HuggingFace Space Locally with Docker

**The BEST self-hosting solution!** Use the official Space's Docker image on your GPU server.

## Why This is Perfect

✅ **Official setup** - HuggingFace already solved all dependencies
✅ **Your GPU** - Runs on your local NVIDIA GPU
✅ **Self-hosted** - Full control, no external API calls
✅ **Pre-configured** - No dependency debugging
✅ **Free** - No HF Inference Endpoint costs
✅ **Working** - Already proven to work in the Space

## Step-by-Step Setup

### 1. Find the Official Space

Go to the official Step1X-3D Space:
- https://huggingface.co/spaces/stepfun-ai/Step1X-3D

Or one of these community Spaces that use Step1X-3D:
- https://huggingface.co/spaces/cavargas10/Step1X-TextureGeneration
- https://huggingface.co/spaces/minhtung/Step1X-3D

### 2. Get Docker Run Command

1. **Click "Run with Docker"** button (top-right corner of the Space page)
2. **Copy the Docker command** shown in the popup

It will look something like:

```bash
docker run -it -p 7860:7860 \
  --platform=linux/amd64 \
  --gpus all \
  registry.hf.space/stepfun-ai-step1x-3d:latest
```

### 3. Login to HuggingFace Docker Registry

```bash
# Get your HF token from: https://huggingface.co/settings/tokens
docker login registry.hf.space -u YOUR_HF_USERNAME -p YOUR_HF_TOKEN
```

### 4. Run on Your Server

```bash
# Pull the image
docker pull registry.hf.space/stepfun-ai-step1x-3d:latest

# Run with GPU
docker run -d \
  --name step1x3d \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/output:/app/output \
  registry.hf.space/stepfun-ai-step1x-3d:latest
```

### 5. Access the UI

Open in your browser:
- `http://localhost:7860` (on server)
- `http://your-server-ip:7860` (from other machines)

## Complete Setup Script

I've created `run-hf-space.sh` for you:

```bash
./run-hf-space.sh
```

This will:
1. Check Docker and GPU access
2. Login to HF registry
3. Pull the Space image
4. Run it on your GPU
5. Show you the access URL

## Advantages

| Feature | HF Space Docker | Self-build Docker | Native Setup |
|---------|----------------|-------------------|--------------|
| Dependency management | ✅ Done by HF | ❌ You debug | ❌ You debug |
| Setup time | 5 minutes | Hours/days | Hours/days |
| Uses your GPU | ✅ Yes | ✅ Yes | ✅ Yes |
| Self-hosted | ✅ Yes | ✅ Yes | ✅ Yes |
| Cost | Free | Free | Free |
| Updates | Easy (pull new image) | Rebuild | Reinstall |
| Working guarantee | ✅ HF tested | ⚠️ May break | ⚠️ May break |

## Managing the Container

```bash
# Start
docker start step1x3d

# Stop
docker stop step1x3d

# View logs
docker logs -f step1x3d

# Restart
docker restart step1x3d

# Remove
docker rm -f step1x3d
```

## Updating

```bash
# Pull latest version
docker pull registry.hf.space/stepfun-ai-step1x-3d:latest

# Remove old container
docker rm -f step1x3d

# Run new version
./run-hf-space.sh
```

## Troubleshooting

### Can't access Space page
Some Spaces may be private or moved. Try these alternatives:
- https://huggingface.co/spaces/cavargas10/Step1X-TextureGeneration
- https://huggingface.co/spaces/minhtung/Step1X-3D

### Docker image not found
The Space may not have Docker enabled. Look for Spaces with:
- "Run with Docker" button visible
- Docker icon in the Space card

### GPU not detected in container
```bash
# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Why This is Better Than Building Yourself

**HuggingFace Spaces already solved:**
- ✅ All dependency versions
- ✅ Python environment setup
- ✅ CUDA compatibility
- ✅ Model loading
- ✅ Web UI setup
- ✅ Security hardening
- ✅ Performance optimization

**You get:**
- ✅ Tested, working setup
- ✅ Regular updates from HF
- ✅ Community support
- ✅ Professional deployment

## Cost Comparison

**HF Space Docker (this approach):**
- Setup: 5 minutes
- Your GPU server: $0 (you already have it)
- Total: **FREE + 5 minutes**

**HF Inference Endpoints:**
- Setup: 5 minutes
- Usage: $0.60/hour
- Total: **$432/month if running 24/7**

**Self-build:**
- Setup: Days of debugging
- Your time: $$$
- Your GPU server: $0
- Total: **FREE + days of frustration**

## Perfect For

✅ Development and testing
✅ Internal company use
✅ Full control over infrastructure
✅ Using existing GPU servers
✅ Avoiding recurring API costs
✅ Data privacy (everything local)

## Next Steps

1. Go to the Space page
2. Click "Run with Docker"
3. Follow the instructions
4. Or use the script I created: `./run-hf-space.sh`

This is the **sweet spot** between convenience and control! 🎉

