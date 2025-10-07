#!/bin/bash

# Development Script for Step1X-3D
# Starts backend and frontend in development mode with hot reload

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Get current directory
PROJECT_DIR=$(pwd)
print_status "Project directory: $PROJECT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your HuggingFace token before continuing"
    echo "   nano .env"
    read -p "Press Enter when ready to continue..."
fi

# Function to start backend in development mode
start_backend() {
    print_status "Starting backend in development mode..."
    cd "$PROJECT_DIR/backend"
    
    if [ ! -d ".venv" ]; then
        echo "❌ Backend virtual environment not found. Run setup.sh first."
        exit 1
    fi
    
    source .venv/bin/activate
    
    # Set development environment variables
    export DEBUG=True
    export RELOAD=True
    export LOG_LEVEL=DEBUG
    
    print_success "Backend starting on http://localhost:8000"
    print_success "API docs available at http://localhost:8000/docs"
    
    # Start with hot reload
    python main.py
}

# Function to start frontend in development mode
start_frontend() {
    print_status "Starting frontend in development mode..."
    cd "$PROJECT_DIR/frontend"
    
    if [ ! -d ".venv" ]; then
        echo "❌ Frontend virtual environment not found. Run setup.sh first."
        exit 1
    fi
    
    source .venv/bin/activate
    
    print_success "Frontend starting on http://localhost:8501"
    
    # Start Streamlit with hot reload
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
}

# Function to start both services
start_both() {
    print_status "Starting both services in development mode..."
    
    # Start backend in background
    cd "$PROJECT_DIR"
    start_backend &
    BACKEND_PID=$!
    
    # Wait a moment for backend to start
    sleep 5
    
    # Start frontend
    start_frontend &
    FRONTEND_PID=$!
    
    # Function to cleanup on exit
    cleanup() {
        echo ""
        print_status "Stopping development services..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 0
    }
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    print_success "Both services started!"
    print_success "Backend: http://localhost:8000"
    print_success "Frontend: http://localhost:8501"
    print_success "Press Ctrl+C to stop both services"
    
    # Wait for processes
    wait
}

# Function to show help
show_help() {
    echo "Step1X-3D Development Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  backend    Start only the backend service"
    echo "  frontend   Start only the frontend service"
    echo "  both       Start both services (default)"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start both services"
    echo "  $0 backend      # Start only backend"
    echo "  $0 frontend     # Start only frontend"
    echo ""
    echo "Development features:"
    echo "  - Hot reload enabled"
    echo "  - Debug logging"
    echo "  - Auto-restart on file changes"
    echo ""
    echo "Make sure to run ./scripts/setup.sh first!"
}

# Main script logic
case "${1:-both}" in
    "backend")
        start_backend
        ;;
    "frontend")
        start_frontend
        ;;
    "both"|"")
        start_both
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac
