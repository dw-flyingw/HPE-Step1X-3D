# Why PyTorch 2.5.1 is Required

## The Problem

Step1X-3D code uses this decorator:
```python
@torch.amp.custom_fwd(device_type="cuda")
```

## PyTorch API Evolution

| PyTorch Version | API Location | Status |
|----------------|--------------|--------|
| 2.0 - 2.3 | `torch.cuda.amp.custom_fwd` | Old API ❌ |
| 2.4+ | `torch.amp.custom_fwd(device_type="cuda")` | New unified API ✅ |

## What Happened

1. We installed PyTorch 2.3.1
2. PyTorch 2.3.1 only has `torch.cuda.amp` (old API)
3. Step1X-3D expects `torch.amp` (new API)
4. Result: `AttributeError: module 'torch.amp' has no attribute 'custom_fwd'`

## The Solution

Upgrade to **PyTorch 2.5.1** which has the new unified `torch.amp` API.

- ✅ Compatible with CUDA 11.8
- ✅ Has `torch.amp.custom_fwd` API
- ✅ All other dependencies remain compatible

## Run This on Remote Server

```bash
cd ~/HPE-Step1X-3D

# Option 1: Use the automated script
chmod +x final-fix-pytorch-2.5.sh
./final-fix-pytorch-2.5.sh

# Option 2: Manual commands
cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
trimesh
torch==2.5.1
torchvision==0.20.1
torchaudio==2.5.1
diffusers==0.30.3
transformers==4.42.4
accelerate==0.33.0
bitsandbytes
python-multipart
Jinja2
einops
pytorch-lightning==2.4.0
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

docker compose down
docker rmi $(docker images -q '*backend*') -f
docker compose build --no-cache backend
docker compose up -d backend
docker compose logs -f backend
```

## This Should Be The Final Fix

PyTorch 2.5.1 has everything Step1X-3D needs:
- ✅ `torch.amp.custom_fwd` API
- ✅ CUDA 11.8 support  
- ✅ All modern features
- ✅ Stable release

After this upgrade, the torch.amp error should be resolved!

