# Remote Server Pre-Build Checklist

**For: hpadmin@sut73:~/HPE-Step1X-3D**

Before running `docker compose build backend` on your remote server, complete ALL these steps:

## ❗ CRITICAL: Step1X-3D Code Missing

Your `Step1X-3D/` directory is **EMPTY**. This will cause the build to fail!

### Fix on Remote Server:

SSH to your remote server and run:

```bash
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D

# Clone the Step1X-3D repository
git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D

# Verify it worked
ls -la Step1X-3D/
# Should see: step1x3d_geometry/ directory and other files

# Specifically verify the Python module exists
ls -la Step1X-3D/step1x3d_geometry/
# Should see: __init__.py, models/, data/, systems/, utils/
```

**If git clone doesn't work (firewall/network issues):**

From your **local machine**, copy the Step1X-3D repo to the server:

```bash
# First, clone it locally if you don't have it
git clone https://github.com/stepfun-ai/Step1X-3D.git /tmp/Step1X-3D

# Then copy to remote server
rsync -avz /tmp/Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/Step1X-3D/

# Or using scp
scp -r /tmp/Step1X-3D/* hpadmin@sut73:~/HPE-Step1X-3D/Step1X-3D/
```

## 🔍 Quick Verification on Remote Server

SSH to the server and run this:

```bash
cd ~/HPE-Step1X-3D

# One-line verification
bash << 'VERIFY'
echo "=== Verification ==="
[ -f Step1X-3D/step1x3d_geometry/__init__.py ] && echo "✅ Step1X-3D code present" || echo "❌ Step1X-3D MISSING - CRITICAL!"
[ -d Step1X-3D/step1x3d_geometry/models ] && echo "✅ models/ found" || echo "❌ models/ MISSING"
[ -f backend/requirements.txt ] && echo "✅ requirements.txt present" || echo "❌ requirements.txt MISSING"
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null && echo "✅ GPU accessible" || echo "❌ GPU NOT accessible"
df -h . | tail -1 | awk '{print "💾 Free space: " $4}'
VERIFY
```

## 📋 Complete Pre-Build Checklist

Run these commands on **hpadmin@sut73**:

```bash
cd ~/HPE-Step1X-3D

# 1. Verify Step1X-3D code is present
echo "1. Checking Step1X-3D code..."
if [ -f "Step1X-3D/step1x3d_geometry/__init__.py" ]; then
    echo "   ✅ Step1X-3D code found"
else
    echo "   ❌ STOP! Clone Step1X-3D first:"
    echo "      git clone https://github.com/stepfun-ai/Step1X-3D.git Step1X-3D"
    exit 1
fi

# 2. Check GPU access
echo "2. Checking GPU access..."
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "   ✅ GPU accessible"
else
    echo "   ❌ GPU not accessible - check nvidia-container-toolkit"
fi

# 3. Check disk space (need 20GB+)
echo "3. Checking disk space..."
df -h .

# 4. Verify updated requirements.txt
echo "4. Checking requirements.txt..."
if grep -q "torch==2.3.1" backend/requirements.txt; then
    echo "   ✅ requirements.txt updated"
else
    echo "   ⚠️  requirements.txt may be outdated"
fi

# 5. Create .env if missing
echo "5. Checking .env..."
if [ ! -f .env ]; then
    echo "   Creating .env with defaults..."
    cat > .env << 'EOF'
BACKEND_PORT=8000
FRONTEND_PORT=8501
OUTPUT_DIR=/app/output
BACKEND_URL=http://backend:8000
EOF
    echo "   ✅ .env created"
else
    echo "   ✅ .env exists"
fi

# 6. Create output directory
echo "6. Checking output directory..."
mkdir -p output
chmod 755 output
echo "   ✅ output directory ready"

echo ""
echo "✅ All checks passed! Ready to build."
echo ""
echo "Next steps:"
echo "  docker compose build --no-cache backend"
echo "  docker compose up -d backend"
echo "  docker compose logs -f backend"
```

## ⏱️ What to Expect

### Build Phase (10-20 minutes)
```bash
docker compose build --no-cache backend
```

You'll see:
- Downloading base image (~2 min)
- Installing Python packages (~10-15 min)
- **PyTorch 2.3.1 is large (~2GB)** - be patient!
- Copying Step1X-3D code (<1 min)

### First Startup (10-30 minutes)
```bash
docker compose up -d backend
docker compose logs -f backend
```

You'll see:
1. Container starting
2. **Downloading models from HuggingFace** (~10-25 min on first run)
   - `stepfun-ai/Step1X-3D` with multiple subfolders
   - This is normal! Models are 5-10GB
3. Loading models to GPU (~2-5 min)
4. Server ready: `Application startup complete`

### Subsequent Starts (2-5 minutes)
Models are cached, so future starts are much faster.

## 🚦 When You're Ready

After verifying everything above, run on your **remote server**:

```bash
cd ~/HPE-Step1X-3D

# Build (grab a coffee ☕)
docker compose build --no-cache backend

# Start in detached mode
docker compose up -d backend

# Watch logs (Ctrl+C to exit, container keeps running)
docker compose logs -f backend
```

## 🔧 If Something Goes Wrong

### "ModuleNotFoundError: No module named 'step1x3d_geometry'"
**→ You didn't clone Step1X-3D!** See step 1 above.

### Build gets stuck at "Installing torch..."
**→ Normal!** PyTorch 2.3.1 is ~2GB. Wait 5-10 minutes.

### "Downloading stepfun-ai/Step1X-3D..." takes forever
**→ Normal on first run!** Models are large. Check:
```bash
# On remote server
docker exec backend-1 df -h /root/.cache/huggingface
```

### Container exits with code 1
```bash
# Check logs for the error
docker compose logs backend | tail -50

# Common fixes:
docker compose down
docker compose build --no-cache backend
docker compose up -d backend
```

## 📞 Ready to Build?

**Before you run the build, answer YES to all:**
- [ ] Is Step1X-3D code present in `~/HPE-Step1X-3D/Step1X-3D/`?
- [ ] Can you run `nvidia-smi` successfully in Docker?
- [ ] Do you have 20GB+ free disk space?
- [ ] Is requirements.txt updated with torch==2.3.1?
- [ ] Are you on the remote server (sut73)?

If all YES → Run the build!

If any NO → Fix it first, then build.

