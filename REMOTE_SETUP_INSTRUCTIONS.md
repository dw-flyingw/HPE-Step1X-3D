# Remote Server Setup Instructions

## Quick Start (One Command)

Transfer files to your remote server and run the automated setup:

```bash
# On your local machine:
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/

# SSH to remote server:
ssh hpadmin@sut73

# Run the automated preparation script:
cd ~/HPE-Step1X-3D
chmod +x prepare-remote-backend.sh
./prepare-remote-backend.sh
```

That's it! The script will:
1. ✅ Clone Step1X-3D repository (if missing)
2. ✅ Update requirements.txt with compatible versions
3. ✅ Create .env file with defaults
4. ✅ Create output directory
5. ✅ Verify Docker and GPU access
6. ✅ Check disk space and network
7. ✅ Optionally build and start the backend

## What the Script Does

### Automatic Tasks
- Detects if Step1X-3D code is missing and clones it
- Backs up old requirements.txt
- Updates to torch 2.3.1 and compatible versions
- Creates .env with sensible defaults
- Sets up directory structure
- Verifies all prerequisites

### Interactive Prompts
The script will ask you:
1. If disk space is low - continue anyway?
2. If GPU is not detected - continue anyway?
3. Build the backend now? (yes/no)
4. Start the backend now? (yes/no)

## Manual Method (If Script Fails)

If the automated script has issues, follow these manual steps:

### 1. Clone Step1X-3D
```bash
cd ~/HPE-Step1X-3D
git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D
```

### 2. Update requirements.txt
```bash
cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
trimesh
torch==2.3.1
torchvision==0.18.1
torchaudio==2.3.1
diffusers==0.30.3
transformers==4.42.4
accelerate==0.33.0
bitsandbytes
python-multipart
Jinja2
einops
pytorch-lightning==2.3.3
omegaconf
jaxtyping
typeguard
mosaicml-streaming==0.11.0
timm
pymeshlab
wandb
rembg
onnxruntime
beautifulsoup4
python-dotenv
safetensors==0.4.1
huggingface-hub==0.24.5
numpy<2.0.0
EOF
```

### 3. Create .env
```bash
cat > .env << 'EOF'
BACKEND_PORT=8000
FRONTEND_PORT=8501
OUTPUT_DIR=/app/output
BACKEND_URL=http://backend:8000
EOF
```

### 4. Build and Start
```bash
mkdir -p output
docker compose build --no-cache backend
docker compose up -d backend
docker compose logs -f backend
```

## Verification

After running the script, verify everything is working:

```bash
# Check container status
docker compose ps

# Should see:
# NAME       IMAGE          STATUS
# backend-1  ...backend     Up X seconds

# Check logs
docker compose logs backend | tail -50

# Test the API (after models are loaded)
curl -X POST http://localhost:8000/generate-3d -F 'prompt=test cube'
```

## Timeline

- **Preparation script**: 2-5 minutes
- **Docker build**: 10-20 minutes
- **First startup**: 10-30 minutes (downloading ~5-10GB of models)
- **Subsequent starts**: 2-5 minutes (models cached)

## Troubleshooting

### "git: command not found"
```bash
sudo apt-get update && sudo apt-get install -y git
```

### "Cannot reach huggingface.co"
Check firewall/proxy settings. Models won't download without internet.

### "GPU not accessible"
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Install nvidia-container-toolkit if needed
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Build fails with "No space left on device"
```bash
# Clean Docker
docker system prune -a -f

# Check space
df -h
```

## Additional Scripts

- `remote-verify-setup.sh` - Just verify without making changes
- `rebuild-backend.sh` - Rebuild after code changes
- `REMOTE_QUICK_FIX.sh` - Quick fix for compatibility issues

## Support

If you encounter issues:
1. Check logs: `docker compose logs backend`
2. Run verification: `./remote-verify-setup.sh`
3. Review: `REMOTE_PRE_BUILD_CHECKLIST.md`

