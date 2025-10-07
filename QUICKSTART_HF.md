# Quick Start: HuggingFace Inference Endpoints

## Setup (One Time - 15 minutes)

### 1. Deploy Endpoint on HuggingFace

1. Go to https://ui.endpoints.huggingface.co/
2. Click "New Endpoint"
3. Configure:
   - Model: `stepfun-ai/Step1X-3D`
   - Name: `step1x3d`
   - Instance: GPU Medium (T4)
   - Min replicas: 0 (saves money)
   - Max replicas: 1
4. Click "Create"
5. Wait 5-10 minutes for deployment

### 2. Get Credentials

**Get Access Token:**
- Go to https://huggingface.co/settings/tokens
- Create new token with "Write" access
- Copy the token (starts with `hf_...`)

**Get Endpoint URL:**
- After deployment, copy the endpoint URL
- Looks like: `https://xxxxx.us-east-1.aws.endpoints.huggingface.cloud`

### 3. Setup Client on Remote Server

```bash
# Transfer files
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/

# SSH to server
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D

# Setup (installs minimal dependencies)
./setup-hf-client.sh

# Configure credentials
cat > .env << 'EOF'
HF_TOKEN=hf_your_actual_token_here
HF_ENDPOINT_URL=https://your-actual-endpoint-url.com
EOF
```

### 4. Start Client

```bash
./run-hf-client.sh
```

Access at: `http://your-server:7860`

## Daily Use

```bash
# Start client
./run-hf-client.sh

# Use web UI to generate 3D models

# Stop with Ctrl+C
```

## Advantages

✅ **No local models** - Everything on HuggingFace
✅ **No GPU needed locally** - HF provides the GPU
✅ **No dependency hell** - Just Python + requests
✅ **Auto-scaling** - Scales to zero when idle
✅ **Fully managed** - HF handles everything

## Cost

- **Development**: $0-5/month (with min replicas = 0)
- **Production**: ~$0.60/hour when active
- **First month**: May include free credits

## Troubleshooting

**"503 Service Unavailable"**
- Endpoint is starting up (scaled from zero)
- Wait 30-60 seconds, try again

**"401 Unauthorized"**
- Check HF_TOKEN in .env file
- Verify token has "Write" permissions

**"Endpoint not found"**
- Check HF_ENDPOINT_URL in .env file
- Verify endpoint is deployed and running

## What You Get

- Web UI for uploading images
- Generate 3D models (30-60 seconds)
- Download .glb files
- No local model management!

Perfect for development and testing! 🚀

