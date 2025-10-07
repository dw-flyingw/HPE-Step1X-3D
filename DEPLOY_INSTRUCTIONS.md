# Remote Server Deployment Instructions

## Complete One-Command Deployment

### From Your Local Machine

```bash
# Transfer files to remote server
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/
```

### On Your Remote Server

```bash
# SSH to server
ssh hpadmin@sut73

# Navigate to directory
cd ~/HPE-Step1X-3D

# Run the complete deployment script
chmod +x deploy-remote.sh
./deploy-remote.sh
```

**That's it!** The script will:
1. ✅ Check Python
2. ✅ Install uv
3. ✅ Clean old installations
4. ✅ Setup backend and frontend with uv
5. ✅ Configure .env (prompts for your HF token)
6. ✅ Start both services
7. ✅ Show you the access URLs

## What You Need

Before running the script, have ready:
- **HuggingFace Token**: Get from https://huggingface.co/settings/tokens
  - Create a token with "Read" access
  - Copy the token (starts with `hf_...`)

## After Deployment

### Access the UI
- Open: `http://10.10.0.73:8501` in your browser

### Four Tabs Available:
1. **Generate from Image**: Upload image → Get 3D model
2. **Generate from Prompt**: Text → Image → 3D model
3. **Modify 3D Model**: Upload .glb/.obj/.nii.gz → Convert/modify
4. **View 3D Model**: View stats and convert formats

### Manage Services

```bash
# Check status
./status.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Stop services
./stop.sh

# Restart
./stop.sh && ./start.sh
```

## Ports

- **Frontend (Streamlit)**: 8501
- **Backend (FastAPI)**: 8000

## Firewall

If you need to access from another machine:

```bash
sudo ufw allow 8501/tcp
sudo ufw allow 8000/tcp
```

## Troubleshooting

### Script asks for HF token but you want to skip
- Press Enter when prompted
- Edit .env later: `nano .env`
- Add your token
- Restart: `./start.sh`

### Services won't start
```bash
# Check logs
cat logs/backend.log
cat logs/frontend.log

# Check if venvs created
ls -la backend/.venv
ls -la frontend/.venv
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :8501
sudo lsof -i :8000

# Kill the process or change ports in .env
```

## Manual Steps (if script fails)

If the automated script has issues:

```bash
# 1. Setup
./setup.sh

# 2. Configure
cp env.template .env
nano .env  # Add HF_TOKEN

# 3. Start
./start.sh
```

## File Support

**Generate from:**
- Images (.png, .jpg, .jpeg)
- Text prompts (via Stable Diffusion XL)

**Load/Convert:**
- 3D models (.glb, .obj)
- Medical imaging (.nii.gz)

**Export to:**
- .glb, .obj, .stl, .ply

## Complete!

After deployment, you'll have:
- ✅ Web UI running on port 8501
- ✅ Backend API on port 8000
- ✅ All 4 features working
- ✅ File conversion utilities

Just run `./deploy-remote.sh` and follow the prompts! 🚀

