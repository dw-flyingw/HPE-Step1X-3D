#!/bin/bash

# Deployment Script for Step1X-3D
# Deploys the application to a remote Ubuntu server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_DIR=$(pwd)
REMOTE_USER="${REMOTE_USER:-hpadmin}"
REMOTE_HOST="${REMOTE_HOST:-sut73}"
REMOTE_PATH="${REMOTE_PATH:-~/HPE-Step1X-3D}"

# Function to show help
show_help() {
    echo "Step1X-3D Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -u, --user USER     Remote username (default: $REMOTE_USER)"
    echo "  -h, --host HOST     Remote hostname/IP (default: $REMOTE_HOST)"
    echo "  -p, --path PATH     Remote path (default: $REMOTE_PATH)"
    echo "  --setup-only        Only run setup, don't start services"
    echo "  --start-only        Only start services, skip setup"
    echo "  --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  REMOTE_USER         Remote username"
    echo "  REMOTE_HOST         Remote hostname/IP"
    echo "  REMOTE_PATH         Remote deployment path"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy to default server"
    echo "  $0 -h 192.168.1.100 -u ubuntu        # Deploy to custom server"
    echo "  $0 --setup-only                      # Only run setup"
    echo "  $0 --start-only                      # Only start services"
    echo ""
}

# Parse command line arguments
SETUP_ONLY=false
START_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--user)
            REMOTE_USER="$2"
            shift 2
            ;;
        -h|--host)
            REMOTE_HOST="$2"
            shift 2
            ;;
        -p|--path)
            REMOTE_PATH="$2"
            shift 2
            ;;
        --setup-only)
            SETUP_ONLY=true
            shift
            ;;
        --start-only)
            START_ONLY=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate configuration
if [ -z "$REMOTE_HOST" ] || [ -z "$REMOTE_USER" ]; then
    print_error "Remote host and user must be specified"
    show_help
    exit 1
fi

print_status "Deployment Configuration:"
echo "  Remote Host: $REMOTE_HOST"
echo "  Remote User: $REMOTE_USER"
echo "  Remote Path: $REMOTE_PATH"
echo "  Project Dir: $PROJECT_DIR"
echo ""

# Function to run command on remote server
run_remote() {
    ssh "$REMOTE_USER@$REMOTE_HOST" "$@"
}

# Function to copy files to remote server
copy_files() {
    print_status "Copying files to remote server..."
    
    # Create .rsyncignore file
    cat > .rsyncignore << EOF
.git/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
backup/
*.log
EOF
    
    # Sync files
    rsync -avz --delete \
        --exclude-from=.rsyncignore \
        --exclude='.git/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='.venv/' \
        --exclude='backup/' \
        "$PROJECT_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"
    
    rm .rsyncignore
    print_success "Files copied successfully"
}

# Function to setup remote server
setup_remote() {
    print_status "Setting up remote server..."
    
    # Make setup script executable and run it
    run_remote "cd $REMOTE_PATH && chmod +x scripts/setup.sh && ./scripts/setup.sh"
    
    print_success "Remote setup completed"
}

# Function to start services on remote server
start_services() {
    print_status "Starting services on remote server..."
    
    # Start services
    run_remote "cd $REMOTE_PATH && ./scripts/start.sh"
    
    # Wait a moment for services to start
    sleep 10
    
    # Check service status
    print_status "Checking service status..."
    run_remote "cd $REMOTE_PATH && ./scripts/status.sh"
    
    print_success "Services started successfully"
}

# Function to get server information
get_server_info() {
    print_status "Getting server information..."
    
    # Get server IP
    SERVER_IP=$(run_remote "hostname -I | awk '{print \$1}'")
    
    print_success "Deployment completed successfully!"
    echo ""
    echo "🌐 Access Information:"
    echo "  Frontend: http://$SERVER_IP:8501"
    echo "  Backend:  http://$SERVER_IP:8000"
    echo "  API Docs: http://$SERVER_IP:8000/docs"
    echo ""
    echo "🔧 Management Commands:"
    echo "  SSH to server: ssh $REMOTE_USER@$REMOTE_HOST"
    echo "  Check status:  ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && ./scripts/status.sh'"
    echo "  View logs:     ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && ./scripts/logs.sh'"
    echo "  Stop services: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && ./scripts/stop.sh'"
    echo "  Start services: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && ./scripts/start.sh'"
    echo ""
}

# Main deployment logic
main() {
    print_status "Starting deployment to $REMOTE_USER@$REMOTE_HOST..."
    
    # Check if we can connect to remote server
    print_status "Testing connection to remote server..."
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$REMOTE_USER@$REMOTE_HOST" exit 2>/dev/null; then
        print_error "Cannot connect to remote server. Please check:"
        echo "  1. Server is reachable: ping $REMOTE_HOST"
        echo "  2. SSH key is set up: ssh-copy-id $REMOTE_USER@$REMOTE_HOST"
        echo "  3. Username and hostname are correct"
        exit 1
    fi
    print_success "Connection to remote server successful"
    
    if [ "$START_ONLY" = false ]; then
        # Copy files
        copy_files
        
        # Setup remote server
        setup_remote
    fi
    
    if [ "$SETUP_ONLY" = false ]; then
        # Start services
        start_services
        
        # Get server information
        get_server_info
    else
        print_success "Setup completed. Run with --start-only to start services."
    fi
}

# Run main function
main
