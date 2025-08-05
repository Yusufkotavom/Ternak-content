#!/bin/bash

# Auto Content Generator Restore Script

# Configuration
BACKUP_DIR="/backup"
APP_DIR="/opt/auto-content-generator"
RESTORE_USER="www-data"
RESTORE_GROUP="www-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to show usage
usage() {
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 auto-content-generator_20231201_143022.tar.gz"
    exit 1
}

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    usage
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file $BACKUP_FILE not found in $BACKUP_DIR${NC}"
    echo -e "${YELLOW}Available backups:${NC}"
    ls -la $BACKUP_DIR/auto-content-generator_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

echo -e "${GREEN}Starting restore of Auto Content Generator...${NC}"
echo -e "${YELLOW}Backup file: $BACKUP_FILE${NC}"

# Confirm restore
read -p "Are you sure you want to restore from this backup? This will overwrite the current installation. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Stop the application
echo -e "${YELLOW}Stopping application...${NC}"
systemctl stop auto-content-generator

# Wait for application to stop
sleep 5

# Create backup of current installation
echo -e "${YELLOW}Creating backup of current installation...${NC}"
CURRENT_BACKUP="current_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf $BACKUP_DIR/$CURRENT_BACKUP \
    --exclude=$APP_DIR/venv \
    --exclude=$APP_DIR/__pycache__ \
    --exclude=$APP_DIR/.git \
    $APP_DIR

# Remove current installation
echo -e "${YELLOW}Removing current installation...${NC}"
rm -rf $APP_DIR

# Create app directory
mkdir -p $APP_DIR

# Extract backup
echo -e "${YELLOW}Extracting backup...${NC}"
tar -xzf $BACKUP_DIR/$BACKUP_FILE -C /

# Set correct permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chown -R $RESTORE_USER:$RESTORE_GROUP $APP_DIR
chmod -R 755 $APP_DIR

# Recreate virtual environment
echo -e "${YELLOW}Recreating virtual environment...${NC}"
cd $APP_DIR
sudo -u $RESTORE_USER python3 -m venv venv
sudo -u $RESTORE_USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Start the application
echo -e "${YELLOW}Starting application...${NC}"
systemctl start auto-content-generator

# Wait for application to start
sleep 10

# Check if application started successfully
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}Application restored and started successfully!${NC}"
    echo -e "${GREEN}Application URL: http://localhost:8000${NC}"
else
    echo -e "${RED}Warning: Application may not have started properly${NC}"
    echo -e "${YELLOW}Check logs with: journalctl -u auto-content-generator -f${NC}"
fi

# Clean up current backup
echo -e "${YELLOW}Cleaning up temporary backup...${NC}"
rm -f $BACKUP_DIR/$CURRENT_BACKUP

echo -e "${GREEN}Restore completed!${NC}"