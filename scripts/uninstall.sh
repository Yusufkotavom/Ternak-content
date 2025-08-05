#!/bin/bash

# Auto Content Generator Uninstall Script

# Configuration
APP_DIR="/opt/auto-content-generator"
BACKUP_DIR="/backup"

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

# Function to confirm uninstall
confirm_uninstall() {
    echo ""
    print_warning "This will completely remove Auto Content Generator from your system."
    echo ""
    echo "The following will be removed:"
    echo "- Application files: $APP_DIR"
    echo "- Systemd service: auto-content-generator"
    echo "- Nginx configuration"
    echo "- Supervisor configuration"
    echo "- Cron jobs"
    echo "- Log files: /var/log/auto-content-generator/"
    echo ""
    print_warning "Backups in $BACKUP_DIR will be preserved."
    echo ""
    
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstall cancelled"
        exit 0
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    systemctl stop auto-content-generator 2>/dev/null || true
    systemctl disable auto-content-generator 2>/dev/null || true
    
    print_success "Services stopped"
}

# Function to remove systemd service
remove_systemd_service() {
    print_status "Removing systemd service..."
    
    rm -f /etc/systemd/system/auto-content-generator.service
    systemctl daemon-reload
    
    print_success "Systemd service removed"
}

# Function to remove nginx configuration
remove_nginx_config() {
    print_status "Removing nginx configuration..."
    
    rm -f /etc/nginx/sites-enabled/auto-content-generator
    rm -f /etc/nginx/sites-available/auto-content-generator
    
    # Restart nginx
    systemctl restart nginx 2>/dev/null || true
    
    print_success "Nginx configuration removed"
}

# Function to remove supervisor configuration
remove_supervisor_config() {
    print_status "Removing supervisor configuration..."
    
    rm -f /etc/supervisor/conf.d/auto-content-generator.conf
    
    # Restart supervisor
    systemctl restart supervisor 2>/dev/null || true
    
    print_success "Supervisor configuration removed"
}

# Function to remove cron jobs
remove_cron_jobs() {
    print_status "Removing cron jobs..."
    
    # Remove specific cron jobs
    crontab -l 2>/dev/null | grep -v "auto-content-generator" | grep -v "backup.sh" | grep -v "monitor.sh" | crontab -
    
    print_success "Cron jobs removed"
}

# Function to remove application files
remove_app_files() {
    print_status "Removing application files..."
    
    if [ -d "$APP_DIR" ]; then
        rm -rf $APP_DIR
        print_success "Application files removed"
    else
        print_warning "Application directory not found"
    fi
}

# Function to remove log files
remove_log_files() {
    print_status "Removing log files..."
    
    if [ -d "/var/log/auto-content-generator" ]; then
        rm -rf /var/log/auto-content-generator
        print_success "Log files removed"
    else
        print_warning "Log directory not found"
    fi
}

# Function to remove user and group (if created specifically for this app)
remove_user_group() {
    print_status "Checking for application-specific user/group..."
    
    # Only remove if user/group was created specifically for this app
    # For now, we'll just check and warn
    print_warning "User/group removal skipped (manual check required)"
}

# Function to clean up dependencies (optional)
cleanup_dependencies() {
    print_status "Checking for unused dependencies..."
    
    echo ""
    print_warning "The following packages were installed for Auto Content Generator:"
    echo "- python3, python3-pip, python3-venv"
    echo "- nginx, supervisor, cron"
    echo "- git, curl, wget"
    echo ""
    echo "You may want to remove them if not used by other applications:"
    echo "apt-get remove python3-pip python3-venv nginx supervisor"
    echo ""
}

# Function to display final information
display_final_info() {
    echo ""
    echo "=========================================="
    print_success "Auto Content Generator Uninstall Completed!"
    echo "=========================================="
    echo ""
    echo "The following have been removed:"
    echo "✓ Application files"
    echo "✓ Systemd service"
    echo "✓ Nginx configuration"
    echo "✓ Supervisor configuration"
    echo "✓ Cron jobs"
    echo "✓ Log files"
    echo ""
    print_warning "The following have been preserved:"
    echo "✓ Backups in $BACKUP_DIR"
    echo "✓ System packages (manual removal required)"
    echo ""
    print_status "To completely clean up, you may want to:"
    echo "1. Remove unused system packages"
    echo "2. Clean up any remaining configuration files"
    echo "3. Remove any database files if used"
    echo ""
}

# Function to create backup before uninstall
create_backup() {
    print_status "Creating backup before uninstall..."
    
    if [ -d "$APP_DIR" ]; then
        BACKUP_NAME="pre_uninstall_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf $BACKUP_DIR/$BACKUP_NAME \
            --exclude=$APP_DIR/venv \
            --exclude=$APP_DIR/__pycache__ \
            --exclude=$APP_DIR/.git \
            $APP_DIR
        
        if [ $? -eq 0 ]; then
            print_success "Backup created: $BACKUP_NAME"
        else
            print_warning "Backup creation failed"
        fi
    else
        print_warning "No application directory to backup"
    fi
}

# Main uninstall function
main() {
    print_status "Starting Auto Content Generator uninstall..."
    
    # Check if running as root
    check_root
    
    # Confirm uninstall
    confirm_uninstall
    
    # Create backup
    create_backup
    
    # Stop services
    stop_services
    
    # Remove systemd service
    remove_systemd_service
    
    # Remove nginx configuration
    remove_nginx_config
    
    # Remove supervisor configuration
    remove_supervisor_config
    
    # Remove cron jobs
    remove_cron_jobs
    
    # Remove application files
    remove_app_files
    
    # Remove log files
    remove_log_files
    
    # Remove user/group (optional)
    remove_user_group
    
    # Cleanup dependencies
    cleanup_dependencies
    
    # Display final information
    display_final_info
}

# Run main function
main