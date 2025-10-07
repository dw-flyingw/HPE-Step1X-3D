# Git Workflow Guide

## Overview

This project uses a simple Git-based workflow:
- **MacBook**: Development, commit, push to GitHub
- **Ubuntu Server**: Pull from GitHub, run scripts

## Initial Commit (MacBook)

```bash
cd /Users/dave/AI/HPE/HPE-Step1X-3D

# Check status
git status

# Add all files
git add .

# Commit with message
git commit -m "Refactor: Complete project restructure with local GPU inference

- Modern FastAPI backend with async patterns
- Streamlit frontend with real-time monitoring
- Local GPU inference for 4x Nvidia L40 GPUs
- Intelligent GPU memory management
- Production-ready with systemd services
- Comprehensive deployment scripts
- Complete documentation

Features:
- Image → 3D generation
- Text → Image → 3D pipeline
- 3D model conversion (GLB, OBJ, STL, PLY)
- Medical imaging support (NIfTI)
- Real-time GPU monitoring
- API documentation

Scripts (run on Ubuntu server):
- install.sh: First-time setup
- update.sh: Update after git pull
- start.sh/stop.sh: Service management
- status.sh: System status
- logs.sh: View logs"

# Push to GitHub
git push origin main
```

## First Deployment (Ubuntu Server)

```bash
# SSH to server
ssh hpadmin@sut73

# Clone repository (first time only)
git clone https://github.com/your-username/HPE-Step1X-3D.git
cd HPE-Step1X-3D

# Run installation
chmod +x scripts/*.sh
./scripts/install.sh

# Configure environment
nano .env
# Add: HF_TOKEN=hf_your_token_here

# Start services
./scripts/start.sh

# Check status
./scripts/status.sh
```

## Daily Development Workflow

### MacBook (Development)

```bash
# 1. Make changes
nano backend/app/services/model_service.py

# 2. Test locally (optional)
# Create a local .env first
cp env.example .env
nano .env  # Add your settings

# 3. Stage changes
git add .

# 4. Commit
git commit -m "Fix: Improve model loading performance"

# 5. Push
git push origin main
```

### Ubuntu Server (Deployment)

```bash
# 1. SSH to server
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D

# 2. Pull changes
git pull origin main

# 3. Update and restart
./scripts/update.sh

# 4. Check status
./scripts/status.sh
```

## Quick Updates (No Dependency Changes)

If you only changed Python code (no new dependencies):

**Ubuntu Server:**
```bash
git pull origin main
./scripts/stop.sh
./scripts/start.sh
```

## Major Updates (Dependency Changes)

If you added/updated dependencies:

**Ubuntu Server:**
```bash
git pull origin main
./scripts/update.sh  # This stops, updates deps, and restarts
```

## Common Git Commands

### MacBook

```bash
# Check status
git status

# View changes
git diff

# Stage specific files
git add backend/app/services/model_service.py

# Stage all changes
git add .

# Commit
git commit -m "Your message"

# Push
git push origin main

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename
```

### Ubuntu Server

```bash
# Pull latest changes
git pull origin main

# Check current status
git status

# View commit history
git log --oneline

# Show current branch
git branch

# Discard local changes (if any)
git reset --hard origin/main
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Fix: GPU memory leak in model service"
git commit -m "Feature: Add support for PLY format export"
git commit -m "Update: Improve error handling in mesh conversion"
git commit -m "Docs: Update installation instructions"

# Categories
# Fix: Bug fixes
# Feature: New features
# Update: Improvements to existing features
# Docs: Documentation changes
# Refactor: Code restructuring
# Test: Test additions or changes
```

## Handling Conflicts

If git pull shows conflicts:

```bash
# On Ubuntu server
git status  # See conflicting files

# Option 1: Keep server changes
git checkout --ours filename

# Option 2: Use incoming changes
git checkout --theirs filename

# Option 3: Accept all incoming
git reset --hard origin/main

# After resolving
git add .
git commit
```

## Branches (Optional)

For experimental features:

**MacBook:**
```bash
# Create feature branch
git checkout -b feature-name

# Make changes and commit
git add .
git commit -m "Feature: Your feature"

# Push feature branch
git push origin feature-name

# Switch back to main
git checkout main

# Merge when ready
git merge feature-name
git push origin main
```

## .gitignore

The following are ignored and won't be committed:
- `.env` (your secrets)
- `.venv/` (virtual environments)
- `__pycache__/` (Python cache)
- `output/` (generated files)
- `cache/` and `models/` (downloaded models)
- `backup/` (old files)

## Backup Important Files

Before major changes, backup your `.env`:

**Ubuntu Server:**
```bash
cp .env .env.backup
# Make changes
# If something breaks:
cp .env.backup .env
./scripts/stop.sh && ./scripts/start.sh
```

## Quick Reference

### MacBook → GitHub
```bash
git add .
git commit -m "Your message"
git push origin main
```

### GitHub → Ubuntu Server
```bash
git pull origin main
./scripts/update.sh
```

### Check Everything
```bash
# MacBook
git status
git log --oneline

# Ubuntu Server
git pull
./scripts/status.sh
./scripts/logs.sh
```

## Troubleshooting

### "Your branch is behind"
```bash
git pull origin main
```

### "Merge conflict"
```bash
git reset --hard origin/main  # Discard local changes
```

### "Permission denied"
```bash
# Setup SSH key for GitHub
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add to GitHub: Settings → SSH Keys
```

### Can't push
```bash
# Check remote
git remote -v

# Set remote if needed
git remote add origin https://github.com/your-username/HPE-Step1X-3D.git
```

## Summary

1. **Develop on MacBook** → commit → push to GitHub
2. **Deploy on Ubuntu Server** → pull from GitHub → run update script
3. Simple and clean workflow!

For more details, see:
- [README.md](README.md) - Main documentation
- [QUICK_START.md](QUICK_START.md) - Quick start guide
