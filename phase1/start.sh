#!/bin/bash

################################################################################
# Revenue API Startup Script
# Starts the Flask application with proper configuration
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_banner() {
    echo "================================================================"
    echo "   REVENUE TRACKING API - STARTUP"
    echo "================================================================"
    echo "   Version: 1.0.0"
    echo "   Phase: 1 - Revenue Agent System"
    echo "================================================================"
    echo ""
}

check_env() {
    log_info "Checking environment configuration..."
    
    if [ ! -f "../.env" ]; then
        log_error ".env file not found!"
        echo "Please create .env file from .env.example:"
        echo "  cp ../.env.example ../.env"
        echo "  nano ../.env"
        exit 1
    fi
    
    log_success "Environment file found"
}

check_dependencies() {
    log_info "Checking Python dependencies..."
    
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    log_info "Installing/updating dependencies..."
    pip install -q -r requirements.txt
    
    log_success "Dependencies ready"
}

check_database() {
    log_info "Checking database..."
    
    # Try to initialize database if needed
    if python src/utils/init_db.py > /dev/null 2>&1; then
        log_success "Database initialized"
    else
        log_error "Database initialization failed"
        echo "Make sure PostgreSQL is running and DATABASE_URL is correct"
    fi
}

start_server() {
    log_info "Starting Flask development server..."
    
    source venv/bin/activate
    
    export FLASK_APP=src.api.app
    export FLASK_ENV=development
    
    echo ""
    log_success "Server starting..."
    echo ""
    echo "================================================================"
    echo "   API Endpoints Available:"
    echo "================================================================"
    echo "   Main:        http://localhost:5000/"
    echo "   Health:      http://localhost:5000/health"
    echo "   Payments:    http://localhost:5000/api/payments"
    echo "   Affiliates:  http://localhost:5000/api/affiliates"
    echo "   Content:     http://localhost:5000/api/content"
    echo "   Marketplace: http://localhost:5000/api/marketplace"
    echo "   Dashboard:   http://localhost:5000/api/dashboard"
    echo "================================================================"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    python src/api/app.py
}

main() {
    print_banner
    check_env
    check_dependencies
    check_database
    start_server
}

main
