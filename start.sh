#!/bin/bash
# Start both backend and frontend

set -e

echo "=========================================="
echo "Starting Step1X-3D Services"
echo "=========================================="
echo ""

# Load environment
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "   Run ./setup.sh first"
    exit 1
fi

source .env

# Create logs directory
mkdir -p logs

echo "Starting Backend (FastAPI) on port ${BACKEND_PORT:-8000}..."

# Start backend
cd backend
source .venv/bin/activate
nohup python3 main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 2

echo ""
echo "Starting Frontend (Streamlit) on port ${FRONTEND_PORT:-8501}..."

# Start frontend
cd frontend
source .venv/bin/activate
nohup streamlit run app.py \
    --server.port ${FRONTEND_PORT:-8501} \
    --server.address 0.0.0.0 \
    --server.headless true \
    > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "✅ Services Running!"
echo "=========================================="
echo ""
echo "Access the UI:"
echo "  http://localhost:${FRONTEND_PORT:-8501}"
echo "  http://$(hostname -I | awk '{print $1}'):${FRONTEND_PORT:-8501}"
echo ""
echo "Backend API:"
echo "  http://localhost:${BACKEND_PORT:-8000}"
echo ""
echo "View logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
echo "Stop services:"
echo "  ./stop.sh"
echo ""

