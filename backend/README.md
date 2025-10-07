# Backend Service

This is the backend service for the HPE Step1X-3D application, providing API endpoints for 3D model generation using the Step1X-3D model.

## Features

- FastAPI-based REST API
- CUDA-enabled for GPU acceleration
- CORS support for frontend integration
- Configurable output directory
- Health check endpoint

## Requirements

- Docker with NVIDIA GPU support
- NVIDIA Container Toolkit
- At least 8GB GPU memory recommended

## Configuration

The backend can be configured using environment variables:

- `BACKEND_PORT`: Port for the backend service (default: 8000)
- `OUTPUT_DIR`: Directory for generated 3D models (default: /app/output)

Create a `.env` file in the project root with your configuration:

```env
BACKEND_PORT=8000
OUTPUT_DIR=/app/output
```

## Building and Running

### Using Docker Compose (Recommended)

From the project root:

```bash
# Build and start the backend service
docker compose up -d backend

# View logs
docker compose logs -f backend

# Stop the service
docker compose down
```

### Using Docker Directly

From the project root:

```bash
# Build the image
docker build -f backend/dockerfile -t hpe-step1x3d-backend .

# Run the container
docker run -d \
  --name hpe-backend \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  hpe-step1x3d-backend

# View logs
docker logs -f hpe-backend

# Stop the container
docker stop hpe-backend
```

## API Endpoints

### Generate 3D Model

**POST** `/generate-3d`

Generate a 3D model from a text prompt.

**Parameters:**
- `prompt` (form-data): Text description of the 3D model to generate

**Response:**
- PLY file containing the generated 3D mesh

**Example:**

```bash
curl -X POST "http://localhost:8000/generate-3d" \
  -F "prompt=a red chair"
```

## Dependencies

See `requirements.txt` for the complete list of Python dependencies.

Key dependencies:
- FastAPI: Web framework
- PyTorch: Deep learning framework
- Diffusers: Diffusion model library
- Transformers: NLP model library
- Trimesh: 3D mesh processing

## Troubleshooting

### CUDA Out of Memory

If you encounter CUDA out of memory errors:
1. Reduce batch size
2. Use a GPU with more memory
3. Enable gradient checkpointing

### Module Import Errors

Ensure the `Step1X-3D` directory is properly copied into the container. The `PYTHONPATH` is set to include this directory.

### Output Directory Issues

Ensure the output directory has proper permissions:
```bash
mkdir -p output
chmod 777 output
```

## Development

To modify the backend:

1. Edit `backend/app.py`
2. Rebuild the container: `docker compose build backend`
3. Restart the service: `docker compose up -d backend`

## Notes

- The model weights are downloaded on first run, which may take some time
- GPU acceleration is required for reasonable inference times
- The service automatically creates the output directory if it doesn't exist

