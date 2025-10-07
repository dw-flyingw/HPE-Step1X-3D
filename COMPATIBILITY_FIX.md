# PyTorch/Transformers Compatibility Fix

## Issue

You encountered this error:

```
AttributeError: module 'torch.utils._pytree' has no attribute 'register_pytree_node'
```

This is a **version compatibility issue** between PyTorch and Transformers.

## Root Cause

- PyTorch 2.1.0 was incompatible with the latest transformers library
- Transformers 4.36+ uses `register_pytree_node` which doesn't exist in PyTorch 2.1.x
- Other dependencies also had version conflicts

## Solution Applied

Updated `backend/requirements.txt` with tested, compatible versions:

- **PyTorch**: 2.1.0 → 2.1.2
- **Transformers**: latest → 4.35.2 (compatible with PyTorch 2.1.2)
- **Diffusers**: latest → 0.30.3 (newer version without deprecated APIs)
- **Accelerate**: latest → 0.25.0 (compatible version)
- **PyTorch Lightning**: latest → 2.1.3
- **Hugging Face Hub**: pinned to 0.26.2 (compatible with diffusers 0.30.3)
- **NumPy**: constrained to <2.0.0 (PyTorch 2.1.2 not compatible with NumPy 2.x)
- Added: `safetensors==0.4.1`

## How to Fix on Your Remote Server

### Option 1: Quick Fix (Recommended)

Transfer the updated files and rebuild:

```bash
# On your local machine:
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/

# On the remote server:
cd ~/HPE-Step1X-3D
chmod +x rebuild-backend.sh
./rebuild-backend.sh
```

### Option 2: Manual Fix

On your remote server:

```bash
cd ~/HPE-Step1X-3D

# Stop current backend
docker compose down backend

# Remove the old image to force a clean rebuild
docker rmi hpe-step1x-3d-backend || true

# Rebuild with no cache (important!)
docker compose build --no-cache backend

# Start the backend
docker compose up -d backend

# Check logs
docker compose logs -f backend
```

## Why the `--no-cache` Flag?

Using `--no-cache` ensures:
1. All dependencies are reinstalled with the new versions
2. No cached layers with old package versions are reused
3. Clean build from scratch

## Verify the Fix

After rebuilding, check that the container starts successfully:

```bash
# Check container status
docker compose ps

# Should see:
# NAME                IMAGE                   STATUS
# backend-1           hpe-step1x-3d-backend   Up X seconds

# Check logs (should not see the AttributeError)
docker compose logs backend | grep -i error

# Test the API
curl -X POST http://localhost:8000/generate-3d -F 'prompt=test'
```

## Version Compatibility Matrix

These versions are tested and compatible:

| Package | Version | Notes |
|---------|---------|-------|
| PyTorch | 2.1.2 | CUDA 11.8 compatible |
| Transformers | 4.35.2 | Compatible with PyTorch 2.1.2 |
| Diffusers | 0.30.3 | No deprecated APIs, compatible with modern huggingface-hub |
| Accelerate | 0.25.0 | Compatible with above |
| Hugging Face Hub | 0.26.2 | Compatible with diffusers 0.30.3 |
| NumPy | <2.0.0 | PyTorch 2.1.2 requires NumPy 1.x |

## Future Updates

If you need to update packages in the future:

1. **Always check compatibility** between PyTorch, Transformers, and Diffusers
2. **Pin versions** in requirements.txt (don't use `latest` or no version)
3. **Test locally** before deploying to remote server
4. **Use `--no-cache`** when changing dependencies

## Troubleshooting

### Build Still Fails

If the rebuild still fails:

```bash
# Clean everything
docker compose down -v
docker system prune -a -f

# Rebuild
cd ~/HPE-Step1X-3D
./build-backend.sh
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker
docker system df
docker system prune -a -f --volumes
```

### Need Different PyTorch Version

If you need a different CUDA version:

- CUDA 11.8: `torch==2.1.2+cu118`
- CUDA 12.1: `torch==2.1.2+cu121`

Update the Dockerfile to match your NVIDIA CUDA version.

