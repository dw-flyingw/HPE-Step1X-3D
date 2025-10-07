# Step1X-3D Self-Hosting

Self-host the [Step1X-3D](https://huggingface.co/stepfun-ai/Step1X-3D) model on your own GPU server using HuggingFace's official Space Docker images.

## Quick Start

### Option 1: Run HF Space Locally (Recommended) 🚀

Use the official HuggingFace Space Docker image on your GPU:

```bash
./run-hf-space.sh
```

**Benefits:**
- ✅ Uses your local GPU
- ✅ Pre-configured by HuggingFace
- ✅ No dependency debugging
- ✅ Self-hosted (no API costs)
- ✅ 5-minute setup

**See:** `RUN_HF_SPACE_LOCALLY.md`

### Option 2: HF Inference Endpoints API

Use HuggingFace's managed inference API from your server:

```bash
# Setup
./setup-hf-client.sh

# Configure .env with your HF credentials
cp env.example .env
# Edit .env with your token and endpoint URL

# Run client
./run-hf-client.sh
```

**Benefits:**
- ✅ Fully managed infrastructure
- ✅ Auto-scaling
- ✅ No local GPU needed
- ✅ Simple Python client

**See:** `HF_INFERENCE_ENDPOINTS_GUIDE.md` and `QUICKSTART_HF.md`

## What's Included

```
├── client/
│   └── gradio_client.py          # API client for HF Endpoints
├── env.example                    # Configuration template
├── setup-hf-client.sh            # Setup script for API client
├── run-hf-client.sh              # Run API client
├── run-hf-space.sh               # Run HF Space Docker image
├── RUN_HF_SPACE_LOCALLY.md       # Complete guide for Option 1
├── HF_INFERENCE_ENDPOINTS_GUIDE.md # Complete guide for Option 2
└── QUICKSTART_HF.md              # Quick reference
```

## Requirements

### For Option 1 (HF Space Docker):
- Docker with GPU support
- NVIDIA GPU (8GB+ VRAM)
- nvidia-container-toolkit
- HuggingFace account

### For Option 2 (HF Endpoints API):
- Python 3.8+
- HuggingFace account
- Internet connection

## Documentation

- **`RUN_HF_SPACE_LOCALLY.md`** - Complete guide for running HF Space locally
- **`HF_INFERENCE_ENDPOINTS_GUIDE.md`** - Setup guide for managed endpoints
- **`QUICKSTART_HF.md`** - Quick reference for both options

## Why This Approach?

We tried multiple approaches and found that using HuggingFace's official infrastructure (either the Space Docker image or managed endpoints) is far superior to building from scratch:

| Approach | Setup Time | Maintenance | Cost |
|----------|-----------|-------------|------|
| HF Space Docker | 5 min | Easy | Free (your GPU) |
| HF Endpoints | 5 min | Zero | ~$0.60/hr |
| Self-build | Days | Hard | Time $$$$ |

## Getting Started

**Recommended:** Start with Option 1 (HF Space Docker)

```bash
# On your GPU server
./run-hf-space.sh
```

Access at: `http://your-server:7860`

That's it! 🎉

## Support

- Model Page: https://huggingface.co/stepfun-ai/Step1X-3D
- HF Spaces: https://huggingface.co/spaces/stepfun-ai/Step1X-3D
- HF Endpoints: https://ui.endpoints.huggingface.co/

