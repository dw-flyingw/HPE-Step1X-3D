# Backend Rebuild Guide

## When to Use Each Script

### 🚀 `restart-backend.sh` - Fastest (seconds)
**When:** No code or config changes, just restart the container

```bash
./restart-backend.sh
```

**Use for:**
- Container crashed and you want to restart it
- Changed .env file
- Testing after clearing cache/data
- Quick restart to free memory

**Time:** ~5 seconds

---

### ⚡ `rebuild-fast.sh` - Fast (1-3 minutes)
**When:** You changed code (app.py) but NOT dependencies

```bash
./rebuild-fast.sh
```

**Use for:**
- Modified `backend/app.py`
- Changed Step1X-3D code
- Fixed bugs in Python code
- Updated API endpoints

**What it does:**
- Uses Docker cache for layers
- Only rebuilds from where code changed
- Much faster than full rebuild

**Time:** ~1-3 minutes

**DO NOT use when:**
- ❌ Changed requirements.txt
- ❌ Dependency issues

---

### 🐢 `rebuild-full.sh` - Slow (10-20 minutes)
**When:** You changed requirements.txt or fixing dependency issues

```bash
./rebuild-full.sh
```

**Use for:**
- Changed `requirements.txt` (package versions)
- Fixing PyTorch/dependency version issues
- Cache is causing problems
- First-time build

**What it does:**
- Removes old images
- Builds with `--no-cache`
- Installs all dependencies fresh
- Guarantees clean state

**Time:** ~10-20 minutes

---

## Quick Reference

```bash
# Just restart (no rebuild)
./restart-backend.sh                    # 5 seconds

# Code changes only
./rebuild-fast.sh                       # 1-3 minutes

# Dependency changes or fixing issues
./rebuild-full.sh                       # 10-20 minutes

# Manual commands
docker compose restart backend          # Just restart
docker compose build backend            # Fast rebuild (with cache)
docker compose build --no-cache backend # Full rebuild (no cache)
```

## Examples

### Scenario 1: You fixed a bug in app.py
```bash
# Edit app.py
vim backend/app.py

# Fast rebuild
./rebuild-fast.sh
```

### Scenario 2: You updated a dependency version
```bash
# Edit requirements.txt
vim backend/requirements.txt

# Full rebuild (required!)
./rebuild-full.sh
```

### Scenario 3: Container crashed
```bash
# Just restart
./restart-backend.sh

# Or check logs first
docker compose logs backend
docker compose restart backend
```

### Scenario 4: Changed .env configuration
```bash
# Edit .env
vim .env

# Just restart (no rebuild needed)
./restart-backend.sh
```

## Why Docker Cache Matters

### With Cache (Fast)
```
Step 1/11: Base image        [CACHED]  0s
Step 2/11: Install packages  [CACHED]  0s  ⚡ Reuses old layer
Step 3/11: Install Python    [CACHED]  0s  ⚡ Reuses old layer
Step 4/11: Copy code         [NEW]     5s  ✅ Only rebuilds from here
```
**Total: ~1-3 minutes**

### Without Cache (Slow)
```
Step 1/11: Base image        [BUILD]   30s
Step 2/11: Install packages  [BUILD]   60s
Step 3/11: Install Python    [BUILD]  600s  ⏳ Reinstalls PyTorch
Step 4/11: Copy code         [BUILD]    5s
```
**Total: ~10-20 minutes**

## When Cache Can Cause Problems

Sometimes Docker cache gets "confused" and uses old layers when it shouldn't:

**Symptoms:**
- Old dependency versions still present
- Changes to requirements.txt not taking effect
- Weird import errors that shouldn't happen

**Solution:** Use full rebuild
```bash
./rebuild-full.sh
```

## Pro Tips

1. **After fixing PyTorch version once:** Use fast rebuilds for all future code changes
2. **Check what changed:** `git diff` to see if requirements.txt was modified
3. **Save time:** Use restart when possible, fast rebuild for code, full rebuild only when necessary
4. **CI/CD:** Always use `--no-cache` in production deployments

## Current Status (After PyTorch 2.5.1 Fix)

✅ **Once PyTorch 2.5.1 is installed correctly:**
- Use `./rebuild-fast.sh` for app.py changes
- Use `./restart-backend.sh` for quick restarts
- Only use `./rebuild-full.sh` if you change requirements.txt again

## Decision Tree

```
Did you change requirements.txt?
├─ Yes → Use rebuild-full.sh (10-20 min) 🐢
└─ No
   ├─ Did you change code (app.py)?
   │  ├─ Yes → Use rebuild-fast.sh (1-3 min) ⚡
   │  └─ No → Use restart-backend.sh (5 sec) 🚀
   └─ Is cache causing issues?
      └─ Yes → Use rebuild-full.sh (10-20 min) 🐢
```

