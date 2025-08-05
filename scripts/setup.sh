#!/bin/bash

# Auto Content Generator Setup Script

# Configuration
APP_DIR="/opt/auto-content-generator"
APP_USER="www-data"
APP_GROUP="www-data"
REPO_URL="https://github.com/yourusername/auto-content-eeat.git"

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

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get upgrade -y
    elif command -v yum &> /dev/null; then
        yum update -y
    else
        print_warning "Unknown package manager. Please update manually."
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            git \
            curl \
            wget \
            nginx \
            supervisor \
            cron \
            mailutils \
            bc
    elif command -v yum &> /dev/null; then
        yum install -y \
            python3 \
            python3-pip \
            git \
            curl \
            wget \
            nginx \
            supervisor \
            cronie \
            mailx \
            bc
    else
        print_error "Unsupported operating system"
        exit 1
    fi
}

# Function to create application directory
create_app_directory() {
    print_status "Creating application directory..."
    
    mkdir -p $APP_DIR
    chown $APP_USER:$APP_GROUP $APP_DIR
    chmod 755 $APP_DIR
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    cd $APP_DIR
    sudo -u $APP_USER git clone $REPO_URL .
    
    if [ $? -eq 0 ]; then
        print_success "Repository cloned successfully"
    else
        print_error "Failed to clone repository"
        exit 1
    fi
}

# Function to setup virtual environment
setup_virtual_environment() {
    print_status "Setting up Python virtual environment..."
    
    cd $APP_DIR
    sudo -u $APP_USER python3 -m venv venv
    
    # Activate virtual environment and install dependencies
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt
    
    print_success "Virtual environment setup completed"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "$APP_DIR/.env" ]; then
        cp $APP_DIR/.env.example $APP_DIR/.env
        chown $APP_USER:$APP_GROUP $APP_DIR/.env
        chmod 600 $APP_DIR/.env
        
        print_warning "Please edit $APP_DIR/.env with your API keys and configuration"
    else
        print_status "Environment file already exists"
    fi
}

# Function to setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    cp $APP_DIR/auto-content-generator.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable auto-content-generator
    
    print_success "Systemd service configured"
}

# Function to setup nginx
setup_nginx() {
    print_status "Setting up nginx..."
    
    # Copy nginx configuration
    cp $APP_DIR/nginx.conf /etc/nginx/sites-available/auto-content-generator
    
    # Enable site
    ln -sf /etc/nginx/sites-available/auto-content-generator /etc/nginx/sites-enabled/
    
    # Remove default site if exists
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    if [ $? -eq 0 ]; then
        systemctl enable nginx
        systemctl restart nginx
        print_success "Nginx configured and started"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Function to setup supervisor
setup_supervisor() {
    print_status "Setting up supervisor..."
    
    cp $APP_DIR/supervisor.conf /etc/supervisor/conf.d/auto-content-generator.conf
    
    # Create log directory
    mkdir -p /var/log/auto-content-generator
    chown $APP_USER:$APP_GROUP /var/log/auto-content-generator
    
    systemctl enable supervisor
    systemctl restart supervisor
    
    print_success "Supervisor configured"
}

# Function to setup cron jobs
setup_cron() {
    print_status "Setting up cron jobs..."
    
    # Create backup directory
    mkdir -p /backup
    chown $APP_USER:$APP_GROUP /backup
    
    # Add cron jobs
    (crontab -l 2>/dev/null; echo "0 9 * * * cd $APP_DIR && python cli.py --csv daily_keywords.csv --output /var/www/html/content") | crontab -
    (crontab -l 2>/dev/null; echo "0 23 * * * $APP_DIR/scripts/backup.sh") | crontab -
    (crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/scripts/monitor.sh") | crontab -
    
    print_success "Cron jobs configured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Make scripts executable
    chmod +x $APP_DIR/scripts/*.sh
    
    # Create log directory
    mkdir -p /var/log/auto-content-generator
    chown $APP_USER:$APP_GROUP /var/log/auto-content-generator
    
    print_success "Monitoring setup completed"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    systemctl start auto-content-generator
    systemctl start nginx
    systemctl start supervisor
    
    # Wait for application to start
    sleep 10
    
    # Check if application is running
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Application started successfully"
    else
        print_warning "Application may not have started properly. Check logs with: journalctl -u auto-content-generator -f"
    fi
}

# Function to display final information
display_final_info() {
    echo ""
    echo "=========================================="
    print_success "Auto Content Generator Setup Completed!"
    echo "=========================================="
    echo ""
    echo "Application URL: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
    echo ""
    echo "Important files:"
    echo "- Configuration: $APP_DIR/.env"
    echo "- Logs: /var/log/auto-content-generator/"
    echo "- Backups: /backup/"
    echo ""
    echo "Useful commands:"
    echo "- Check status: systemctl status auto-content-generator"
    echo "- View logs: journalctl -u auto-content-generator -f"
    echo "- Manual backup: $APP_DIR/scripts/backup.sh"
    echo "- Manual restore: $APP_DIR/scripts/restore.sh <backup_file>"
    echo "- Monitor: $APP_DIR/scripts/monitor.sh"
    echo ""
    print_warning "Don't forget to:"
    echo "1. Edit $APP_DIR/.env with your API keys"
    echo "2. Configure your domain in nginx.conf"
    echo "3. Set up SSL certificate for production"
    echo "4. Configure backup retention policy"
    echo ""
}

# Main setup function
main() {
    print_status "Starting Auto Content Generator setup..."
    
    # Check if running as root
    check_root
    
    # Update system
    update_system
    
    # Install dependencies
    install_dependencies
    
    # Create application directory
    create_app_directory
    
    # Clone repository
    clone_repository
    
    # Setup virtual environment
    setup_virtual_environment
    
    # Setup environment file
    setup_environment
    
    # Setup systemd service
    setup_systemd_service
    
    # Setup nginx
    setup_nginx
    
    # Setup supervisor
    setup_supervisor
    
    # Setup cron jobs
    setup_cron
    
    # Setup monitoring
    setup_monitoring
    
    # Start services
    start_services
    
    # Display final information
    display_final_info
}

# Run main function
main