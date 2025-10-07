# Emergency Fix: Torch Version Issue

## Problem

You're still seeing:
```
AttributeError: module 'torch.amp' has no attribute 'custom_fwd'
```

This means **PyTorch 2.1.x is still installed** instead of 2.3.1.

## Root Cause

Docker used **cached layers** from the previous build that had torch 2.1.x, so even though requirements.txt was updated, the old version is still in the container.

## Solution

Run this on your **remote server** (sut73):

### Option 1: Automated Fix (Recommended)

```bash
cd ~/HPE-Step1X-3D

# Transfer the fix script if needed
# (or it should already be there if you rsync'd)

# Run the emergency fix
chmod +x fix-torch-version.sh
./fix-torch-version.sh
```

This script will:
1. ✅ Verify/update requirements.txt
2. ✅ Stop backend
3. ✅ Remove ALL old images (force clean slate)
4. ✅ Build with `--no-cache --pull` (ensures fresh build)
5. ✅ Verify torch version in the new image
6. ✅ Start backend
7. ✅ Show logs

### Option 2: Manual Fix

If the script fails, do this manually:

```bash
cd ~/HPE-Step1X-3D

# 1. Stop backend
docker compose down backend

# 2. Remove ALL backend images (critical!)
docker rmi $(docker images -q '*backend*') -f
docker system prune -f

# 3. Verify requirements.txt has torch 2.3.1
grep "torch==" backend/requirements.txt
# Should show: torch==2.3.1

# If not, update it:
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

# 4. Build with NO CACHE (absolutely critical!)
DOCKER_BUILDKIT=1 docker compose build --no-cache --pull backend

# 5. Verify torch version
docker run --rm hpe-step1x-3d-backend python3 -c "import torch; print('Torch version:', torch.__version__)"
# Should show: Torch version: 2.3.1

# 6. Start backend
docker compose up -d backend

# 7. Monitor logs
docker compose logs -f backend
```

## Verification

After the fix, you should see in the logs:
- ✅ No more `AttributeError: module 'torch.amp' has no attribute 'custom_fwd'`
- ✅ Container continues to run (not exiting with code 1)
- ✅ May see "Downloading stepfun-ai/Step1X-3D..." (normal on first run)
- ✅ Eventually: "Application startup complete" or similar

## Why This Happened

Docker caches layers to speed up builds. When you changed requirements.txt, Docker **thought** the cached layer was still valid because:
- The requirements.txt file content changed
- But Docker's layer cache wasn't properly invalidated
- So it used the old layer with torch 2.1.x

The `--no-cache` flag forces Docker to rebuild **everything** from scratch, ensuring torch 2.3.1 actually gets installed.

## Double-Check Commands

```bash
# Check what's actually in requirements.txt
cat backend/requirements.txt | grep torch

# Should show:
# torch==2.3.1
# torchvision==0.18.1
# torchaudio==2.3.1

# Check what's in the running container
docker exec backend-1 python3 -c "import torch; print(torch.__version__)"

# Should show:
# 2.3.1
```

## If It STILL Fails

If you still see the torch.amp error after this:

1. **Check if Step1X-3D code was actually copied:**
   ```bash
   docker exec backend-1 ls -la /app/Step1X-3D/
   ```

2. **Check PYTHONPATH:**
   ```bash
   docker exec backend-1 echo $PYTHONPATH
   ```

3. **Full nuclear option:**
   ```bash
   docker compose down -v
   docker system prune -a -f --volumes
   # This removes EVERYTHING Docker
   # Then rebuild from scratch
   docker compose build --no-cache backend
   ```

