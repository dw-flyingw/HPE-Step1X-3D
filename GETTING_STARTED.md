# Getting Started with Step1X-3D

## Two Easy Ways to Deploy

### 🚀 Option 1: Run HF Space on Your GPU (RECOMMENDED)

**Best for:** Self-hosting with your own GPU

**Setup (5 minutes):**
```bash
# On your GPU server
./run-hf-space.sh
```

Follow the prompts to:
1. Login to HuggingFace Docker registry
2. Choose a Space to run
3. Start the container

**Access:** `http://your-server:7860`

**What you get:**
- Full web UI
- Uses your local GPU
- No dependency setup needed
- Official HF configuration
- **FREE** (just uses your GPU)

---

### 🌐 Option 2: Use HF Inference Endpoints API

**Best for:** Fully managed, no GPU setup needed

**Setup (10 minutes):**

1. **Deploy endpoint** at https://ui.endpoints.huggingface.co/
2. **Get credentials:**
   - Token: https://huggingface.co/settings/tokens
   - Endpoint URL: from the deployed endpoint
3. **Setup client:**
   ```bash
   ./setup-hf-client.sh
   cp env.example .env
   # Edit .env with your token and endpoint URL
   ./run-hf-client.sh
   ```

**Access:** `http://your-server:7860`

**What you get:**
- Web UI for your team
- HF manages the GPU infrastructure
- Auto-scaling (costs $0 when idle)
- **Cost:** ~$0.60/hour when active

---

## Quick Decision Guide

**Choose Option 1 if:**
- ✅ You have an NVIDIA GPU server
- ✅ You want free inference
- ✅ You're okay managing Docker containers

**Choose Option 2 if:**
- ✅ You don't have a GPU
- ✅ You want zero maintenance
- ✅ Budget allows ~$0.60/hour usage

---

## What's in This Repo

```
├── run-hf-space.sh               # Run HF Space locally (Option 1)
├── setup-hf-client.sh            # Setup API client (Option 2)
├── run-hf-client.sh              # Run API client (Option 2)
├── client/gradio_client.py       # API client code
├── env.example                   # Configuration template
├── RUN_HF_SPACE_LOCALLY.md       # Detailed guide for Option 1
├── HF_INFERENCE_ENDPOINTS_GUIDE.md # Detailed guide for Option 2
└── QUICKSTART_HF.md              # Quick reference
```

---

## Need Help?

1. **Option 1 issues?** See `RUN_HF_SPACE_LOCALLY.md`
2. **Option 2 issues?** See `HF_INFERENCE_ENDPOINTS_GUIDE.md`
3. **Quick reference?** See `QUICKSTART_HF.md`

## Model Information

- **Model:** [stepfun-ai/Step1X-3D](https://huggingface.co/stepfun-ai/Step1X-3D)
- **Official Space:** [stepfun-ai/Step1X-3D](https://huggingface.co/spaces/stepfun-ai/Step1X-3D)
- **Input:** Images (not text)
- **Output:** 3D models (.glb format)

---

**Ready?** Transfer files to your server and run `./run-hf-space.sh`! 🎉

