#!/bin/bash

# Setup script to create .env file with default values
# Run this on your remote server before starting the containers

echo "Creating .env file with default configuration..."

cat > .env << 'EOF'
# Backend Configuration
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_PORT=8501

# Output Directory (inside containers)
OUTPUT_DIR=/app/output

# Backend URL (for frontend to connect)
BACKEND_URL=http://backend:8000

# Optional: DICOM Viewer Port (if needed for future features)
DICOM_VIEWER_PORT=8080
EOF

echo "✓ .env file created successfully!"
echo ""
echo "Default configuration:"
echo "  - Backend Port: 8000"
echo "  - Frontend Port: 8501"
echo ""
echo "You can edit .env to customize these values."

