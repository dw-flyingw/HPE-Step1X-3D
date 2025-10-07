# Pre-Build Checklist for HPE Step1X-3D Backend

Before running `docker compose build backend`, make sure you complete ALL these steps:

## ❗ CRITICAL REQUIREMENTS

### 1. Step1X-3D Repository Code ⚠️ **REQUIRED**

The `Step1X-3D/` directory is currently **EMPTY** and needs the actual Step1X-3D code.

**You need to:**

```bash
cd ~/HPE-Step1X-3D

# Option A: Clone the Step1X-3D repository
git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D

# OR Option B: If you already have it elsewhere, copy it
cp -r /path/to/your/Step1X-3D/* Step1X-3D/

# Verify the structure
ls -la Step1X-3D/
# Should see: step1x3d_geometry/ and other files
```

**The backend app.py requires these imports:**
- `step1x3d_geometry.models.pipelines.pipeline_utils`
- `step1x3d_geometry.models.autoencoders.michelangelo_autoencoder`
- `step1x3d_geometry.models.transformers.flux_transformer_1d`
- `step1x3d_geometry.models.conditional_encoders.label_encoder`

**Without the Step1X-3D code, the container will fail to start!**

### 2. System Requirements

#### GPU & CUDA
- ✅ NVIDIA GPU with 8GB+ VRAM (16GB+ recommended)
- ✅ NVIDIA Driver installed
- ✅ nvidia-container-toolkit installed
- ✅ CUDA 11.8 compatible GPU

**Test GPU access:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

#### Disk Space
- Minimum 20GB free space (models are large!)
- PyTorch: ~2GB
- Model weights: 5-10GB (downloaded on first run)
- Build cache: 3-5GB

**Check disk space:**
```bash
df -h
```

#### Memory
- At least 16GB RAM recommended
- Swap space enabled if RAM < 32GB

### 3. Network Requirements

The backend will download large model files from HuggingFace on first run:
- `stepfun-ai/Step1X-3D` (multiple subfolders)
- This requires:
  - ✅ Internet connectivity
  - ✅ Access to huggingface.co
  - ✅ No firewall blocking HuggingFace
  - ⏱️ Time: 10-30 minutes for first download

**Optional: Set HuggingFace token for private models**
```bash
# Add to .env if needed:
echo "HUGGINGFACE_TOKEN=your_token_here" >> .env
```

### 4. File Structure Check

Run this to verify your setup:

```bash
cd ~/HPE-Step1X-3D

# Check essential files exist
echo "Checking file structure..."
[ -f docker-compose.yml ] && echo "✅ docker-compose.yml" || echo "❌ docker-compose.yml MISSING"
[ -f backend/dockerfile ] && echo "✅ backend/dockerfile" || echo "❌ backend/dockerfile MISSING"
[ -f backend/app.py ] && echo "✅ backend/app.py" || echo "❌ backend/app.py MISSING"
[ -f backend/requirements.txt ] && echo "✅ backend/requirements.txt" || echo "❌ backend/requirements.txt MISSING"
[ -d Step1X-3D ] && echo "✅ Step1X-3D/ exists" || echo "❌ Step1X-3D/ MISSING"
[ -f Step1X-3D/step1x3d_geometry/__init__.py ] && echo "✅ Step1X-3D code present" || echo "❌ Step1X-3D code MISSING - CRITICAL!"

# Check Step1X-3D content
if [ -d "Step1X-3D/step1x3d_geometry" ]; then
    echo "✅ step1x3d_geometry module found"
else
    echo "❌ CRITICAL: Step1X-3D/step1x3d_geometry NOT FOUND!"
    echo "   You MUST clone/copy the Step1X-3D repository first!"
fi
```

### 5. Environment Configuration

```bash
# Create .env file if not exists
[ -f .env ] || ./setup-env.sh

# Verify .env
cat .env
```

### 6. Output Directory

```bash
# Create and set permissions
mkdir -p output
chmod 755 output
```

## 🚀 Ready to Build?

Once ALL above items are ✅, run:

```bash
# Build (will take 10-20 minutes)
docker compose build --no-cache backend

# Start
docker compose up -d backend

# Monitor logs
docker compose logs -f backend
```

## ⏱️ Expected Timeline

1. **Build phase**: 10-20 minutes
   - Base image: 1-2 min
   - Python packages: 8-15 min
   - Code copy: <1 min

2. **First startup**: 10-30 minutes
   - Model download: 10-25 min (depends on network)
   - Model loading: 2-5 min (depends on GPU)
   - Server ready: ~30 sec

3. **Subsequent starts**: 2-5 minutes
   - Models cached, just need to load

## 🔍 Troubleshooting

### If build fails with "ModuleNotFoundError: No module named 'step1x3d_geometry'"

**You forgot to clone Step1X-3D!** Go back to step 1.

### If startup hangs after "Loading model..."

- This is normal on first run - models are downloading
- Check logs: `docker compose logs -f backend`
- Check network: `docker exec backend-1 ping huggingface.co`

### If you see "CUDA out of memory"

- Your GPU doesn't have enough memory
- Try closing other GPU applications
- Check: `nvidia-smi`

### If container exits immediately

- Check logs: `docker compose logs backend`
- Common causes:
  - Missing Step1X-3D code
  - Version incompatibility
  - GPU not accessible

## 📋 Quick Verification Script

Save this as `verify-setup.sh`:

```bash
#!/bin/bash
echo "=== HPE Step1X-3D Setup Verification ==="
echo ""

ERRORS=0

# Check Step1X-3D code
if [ ! -f "Step1X-3D/step1x3d_geometry/__init__.py" ]; then
    echo "❌ CRITICAL: Step1X-3D code is missing!"
    echo "   Run: git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D"
    ERRORS=$((ERRORS+1))
else
    echo "✅ Step1X-3D code found"
fi

# Check GPU
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "✅ GPU accessible"
else
    echo "❌ GPU not accessible"
    ERRORS=$((ERRORS+1))
fi

# Check disk space
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -lt 20 ]; then
    echo "⚠️  Warning: Only ${AVAILABLE}GB free (recommend 20GB+)"
else
    echo "✅ Sufficient disk space (${AVAILABLE}GB free)"
fi

# Check .env
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "⚠️  .env file missing (will use defaults)"
fi

# Check output directory
if [ -d "output" ]; then
    echo "✅ output directory exists"
else
    echo "ℹ️  Creating output directory..."
    mkdir -p output
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All critical checks passed!"
    echo "Ready to build: docker compose build --no-cache backend"
else
    echo "❌ $ERRORS critical issue(s) found. Please fix before building."
    exit 1
fi
```

Run it with:
```bash
chmod +x verify-setup.sh
./verify-setup.sh
```

