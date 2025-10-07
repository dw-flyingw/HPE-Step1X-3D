#!/bin/bash

# Stop Step1X-3D Services
# Run this script ON THE UBUNTU SERVER

echo "🛑 Stopping Step1X-3D services..."

# Stop frontend service
sudo systemctl stop step1x3d-frontend.service

# Stop backend service
sudo systemctl stop step1x3d-backend.service

echo "✅ Services stopped"
