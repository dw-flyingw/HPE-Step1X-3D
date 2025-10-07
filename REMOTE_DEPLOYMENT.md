# Remote Server Deployment Guide

This guide helps you deploy the HPE Step1X-3D backend on a remote server.

## Prerequisites

On your remote server, ensure you have:

1. **Docker** (with Compose V2)
   ```bash
   docker --version
   docker compose version
   ```

2. **NVIDIA Docker Support**
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

3. **Sufficient GPU Memory** (8GB+ recommended)

## Deployment Steps

### 1. Transfer Files to Remote Server

From your local machine:

```bash
# Using rsync
rsync -avz --exclude 'output' --exclude '*.pyc' \
  /Users/dave/AI/HPE/HPE-Step1X-3D/ \
  user@your-server:/path/to/HPE-Step1X-3D/

# Or using scp
scp -r /Users/dave/AI/HPE/HPE-Step1X-3D/ \
  user@your-server:/path/to/HPE-Step1X-3D/
```

### 2. SSH to Remote Server

```bash
ssh user@your-server
cd /path/to/HPE-Step1X-3D
```

### 3. Setup Environment and Build the Backend

**Option A: Use the build script (recommended)**

```bash
# Make the script executable (if not already)
chmod +x build-backend.sh

# Run the build script (automatically creates .env and output directory)
./build-backend.sh
```

**Option B: Manual setup**

```bash
# Create environment file (optional but removes warnings)
chmod +x setup-env.sh
./setup-env.sh

# Or manually create .env
cat > .env << 'EOF'
BACKEND_PORT=8000
FRONTEND_PORT=8501
OUTPUT_DIR=/app/output
BACKEND_URL=http://backend:8000
EOF

# Create output directory
mkdir -p output

# Build the image
docker compose build backend

# Start the service
docker compose up -d backend

# Check logs
docker compose logs -f backend
```

### 4. Configure Firewall (if needed)

If you need to access the backend from other machines:

```bash
# Example for UFW (Ubuntu)
sudo ufw allow 8000/tcp

# Example for firewalld (RHEL/CentOS)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 5. Test the API

From the remote server:

```bash
curl -X POST http://localhost:8000/generate-3d \
  -F 'prompt=a red chair'
```

From your local machine (replace `your-server` with actual IP/hostname):

```bash
curl -X POST http://your-server:8000/generate-3d \
  -F 'prompt=a red chair' \
  -o output.ply
```

## Environment Configuration

Create a `.env` file on the remote server if you need custom settings:

```bash
cat > .env << EOF
BACKEND_PORT=8000
OUTPUT_DIR=/app/output
EOF
```

## Monitoring

### View Logs

```bash
# Follow logs in real-time
docker compose logs -f backend

# View last 100 lines
docker compose logs --tail=100 backend

# View logs since a specific time
docker compose logs --since 30m backend
```

### Check Container Status

```bash
# List running containers
docker compose ps

# Check resource usage
docker stats

# Check GPU usage
nvidia-smi
```

## Troubleshooting

### Container Won't Start

```bash
# Check if port is already in use
sudo lsof -i :8000

# Check container logs
docker compose logs backend

# Restart the service
docker compose restart backend
```

### GPU Not Detected

```bash
# Verify NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Check if nvidia-container-toolkit is installed
dpkg -l | grep nvidia-container-toolkit  # Ubuntu/Debian
rpm -qa | grep nvidia-container-toolkit  # RHEL/CentOS
```

### Permission Issues

```bash
# Ensure output directory has correct permissions
chmod 755 output

# Check Docker socket permissions
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

### Out of Memory

```bash
# Monitor GPU memory
watch -n 1 nvidia-smi

# Restart container to free memory
docker compose restart backend

# If needed, stop other GPU processes
```

## Updating the Backend

When you need to update the code:

```bash
# Pull latest changes (if using git)
git pull

# Or transfer updated files
rsync -avz user@local:/path/to/updated/files/ .

# Rebuild and restart
docker compose build backend
docker compose up -d backend

# Clean up old images (optional)
docker image prune -f
```

## Security Considerations

1. **Use HTTPS in Production**: Set up a reverse proxy (nginx, traefik) with SSL/TLS
2. **Restrict CORS**: Update `app.py` to allow only specific origins
3. **Set Up Authentication**: Add API keys or OAuth for production use
4. **Firewall**: Only open necessary ports
5. **Regular Updates**: Keep Docker, NVIDIA drivers, and dependencies updated

## Performance Optimization

### For Better Performance

```bash
# Use Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker compose build backend

# Adjust worker processes if needed
# Edit docker-compose.yml to add:
# command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### For Lower Memory Usage

```bash
# Limit GPU memory per container
# Edit docker-compose.yml to add:
# environment:
#   - CUDA_VISIBLE_DEVICES=0
#   - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## Automated Deployment Script

Save this as `deploy-remote.sh` on your local machine:

```bash
#!/bin/bash
REMOTE_USER="your-user"
REMOTE_HOST="your-server"
REMOTE_PATH="/path/to/HPE-Step1X-3D"

echo "Syncing files to remote server..."
rsync -avz --exclude 'output' --exclude '*.pyc' \
  ./ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

echo "Building and deploying on remote server..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
cd /path/to/HPE-Step1X-3D
docker compose build backend
docker compose up -d backend
docker compose logs --tail=50 backend
EOF

echo "Deployment complete!"
```

## Support

If you encounter issues:

1. Check the logs: `docker compose logs -f backend`
2. Verify GPU access: `nvidia-smi`
3. Check Docker status: `docker compose ps`
4. Review the backend README: `backend/README.md`

