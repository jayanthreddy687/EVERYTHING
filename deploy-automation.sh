#!/bin/bash

# Cloud Shell Deployment Automation Script
# This script automates all the steps from deploy-cloud-shell.md

set -e  # Exit on any error

echo "🚀 Starting Cloud Shell Deployment Automation..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start within expected time"
    return 1
}

# Step 1: Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command_exists curl; then
    print_error "curl is not installed. Please install curl first."
    exit 1
fi

print_success "All prerequisites are installed!"

# Step 2: Stop existing services if running
print_status "Stopping existing services..."
docker-compose down 2>/dev/null || print_warning "No existing services to stop"

# Step 3: Build and start services
print_status "Building and starting services..."
docker-compose up --build -d

# Step 4: Wait for backend to be ready
print_status "Checking backend service..."
if ! wait_for_service "http://localhost:8000/health" "Backend"; then
    print_error "Backend failed to start. Checking logs..."
    docker-compose logs backend
    exit 1
fi

# Step 5: Test backend endpoints
print_status "Testing backend endpoints..."

test_endpoints=(
    "http://localhost:8000/health"
    "http://localhost:8000/scenarios"
    "http://localhost:8000/user"
    "http://localhost:8000/calendar"
)

for endpoint in "${test_endpoints[@]}"; do
    print_status "Testing: $endpoint"
    if response=$(curl -s "$endpoint"); then
        print_success "✓ $endpoint is responding"
        echo "Response: $(echo "$response" | head -c 100)..."
    else
        print_error "✗ $endpoint failed"
        exit 1
    fi
done

# Step 6: Check frontend service
print_status "Checking frontend service..."
if ! wait_for_service "http://localhost:5173" "Frontend"; then
    print_warning "Frontend might not be ready yet, but backend is working"
fi

# Step 7: Test container-to-container communication
print_status "Testing container communication..."
if docker exec everything-ai-frontend curl -s http://backend:8000/health >/dev/null 2>&1; then
    print_success "✓ Frontend can communicate with backend"
else
    print_warning "Frontend cannot reach backend via container name"
fi

# Step 8: Set up environment variables for Cloud Shell
print_status "Setting up environment variables..."

# Detect if we're in Cloud Shell
if [ -f /etc/google-cloud-shell ]; then
    print_status "Detected Cloud Shell environment"
    
    # Try to get external URL (this might not work in all Cloud Shell setups)
    BACKEND_URL="http://localhost:8000"
    
    # Set frontend environment variable
    echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env
    
    print_success "Environment variables set for Cloud Shell"
    print_status "Backend URL: $BACKEND_URL"
else
    print_status "Local development environment detected"
    
    # For local development, use localhost
    echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env
    
    print_success "Environment variables set for local development"
fi

# Step 9: Restart frontend to apply environment variables
print_status "Restarting frontend to apply environment variables..."
docker-compose restart frontend

# Step 10: Final verification
print_status "Performing final verification..."

# Wait a bit for frontend to restart
sleep 5

# Test if frontend is accessible
if curl -s "http://localhost:5173" >/dev/null 2>&1; then
    print_success "✓ Frontend is accessible at http://localhost:5173"
else
    print_warning "Frontend might still be starting up"
fi

# Test API through frontend container
if docker exec everything-ai-frontend curl -s http://backend:8000/health >/dev/null 2>&1; then
    print_success "✓ API calls from frontend container work"
else
    print_error "✗ API calls from frontend container failed"
    print_status "Checking frontend logs..."
    docker-compose logs frontend | tail -10
fi

# Step 11: Display service URLs and next steps
echo ""
echo "=================================================="
echo "🎉 Deployment Complete!"
echo "=================================================="
echo ""
print_status "Service URLs:"
echo "  • Frontend: http://localhost:5173"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo ""
print_status "Useful Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Check status: docker-compose ps"
echo ""

# Step 12: Health check summary
print_status "Health Check Summary:"
echo "  • Backend Health: $(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo 'Unknown')"
echo "  • Frontend Status: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)"
echo "  • Container Communication: $(docker exec everything-ai-frontend curl -s -o /dev/null -w "%{http_code}" http://backend:8000/health 2>/dev/null || echo 'Failed')"
echo ""

print_success "Automation script completed successfully!"
print_status "If you're still experiencing issues, check the logs above or run: docker-compose logs"
