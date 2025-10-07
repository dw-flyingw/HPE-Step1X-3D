# Step1X-3D Inference System

FastAPI backend + Streamlit frontend for [Step1X-3D](https://huggingface.co/stepfun-ai/Step1X-3D) 3D model generation.

## One-Command Deploy

### Copy Files to Server

```bash
rsync -avz /Users/dave/AI/HPE/HPE-Step1X-3D/ hpadmin@sut73:~/HPE-Step1X-3D/
```

### Deploy on Server

```bash
ssh hpadmin@sut73
cd ~/HPE-Step1X-3D
chmod +x deploy-remote.sh
./deploy-remote.sh
```

**That's it!** Follow the prompts to complete deployment.

## Features

- ✅ **Generate from Image**: Upload image → 3D model
- ✅ **Generate from Prompt**: Text → Image (SDXL) → 3D
- ✅ **Modify 3D Model**: Upload .glb/.obj/.nii.gz + prompt
- ✅ **View & Convert**: View stats, convert formats

## File Support

- **Input**: .png, .jpg, .jpeg, .glb, .obj, .nii.gz
- **Output**: .glb, .obj, .stl, .ply

## Access

- **Frontend**: http://your-server:8501
- **Backend**: http://your-server:8000

## Commands

```bash
./deploy-remote.sh  # One-time deploy
./start.sh          # Start services
./stop.sh           # Stop services
./status.sh         # Check status
```

## Requirements

- Python 3.10+
- HuggingFace token (from https://huggingface.co/settings/tokens)
- Internet connection

See `DEPLOY_INSTRUCTIONS.md` for complete guide.
