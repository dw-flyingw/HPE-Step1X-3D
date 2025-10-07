# Step1X-3D Self-Hosting

Self-host the [Step1X-3D](https://huggingface.co/stepfun-ai/Step1X-3D) model using HuggingFace infrastructure.

## Quick Start

### ⭐ Option 1: HF Inference Endpoints (RECOMMENDED)

Use HuggingFace's fully managed service:

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

### Option 2: Try Community Space Docker Images

Some community Spaces may have Docker support:

```bash
./try-other-spaces.sh
```

This will try pulling from:
- cavargas10/Step1X-TextureGeneration
- minhtung/Step1X-3D
- Others

**Note:** The official stepfun-ai/Step1X-3D Space doesn't publish a Docker image.

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

### For Option 1 (HF Endpoints):
- HuggingFace account
- Access token
- Internet connection
- ~$0.60/hour usage cost (scales to $0 when idle)

### For Option 2 (Community Space Docker):
- Docker with GPU support
- NVIDIA GPU (8GB+ VRAM)
- nvidia-container-toolkit
- HuggingFace account

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

**Recommended:** Use HF Inference Endpoints

See `QUICKSTART_HF.md` for step-by-step instructions.

**Alternative:** Try finding a community Space with Docker support:

```bash
./try-other-spaces.sh
```

## Support

- Model Page: https://huggingface.co/stepfun-ai/Step1X-3D
- HF Spaces: https://huggingface.co/spaces/stepfun-ai/Step1X-3D
- HF Endpoints: https://ui.endpoints.huggingface.co/

