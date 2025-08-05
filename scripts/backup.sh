#!/bin/bash

# Auto Content Generator Backup Script

# Configuration
BACKUP_DIR="/backup"
APP_DIR="/opt/auto-content-generator"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="auto-content-generator_$DATE.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting backup of Auto Content Generator...${NC}"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Stop the application temporarily
echo -e "${YELLOW}Stopping application...${NC}"
systemctl stop auto-content-generator

# Wait a moment for the application to stop
sleep 5

# Create backup
echo -e "${YELLOW}Creating backup...${NC}"
tar -czf $BACKUP_DIR/$BACKUP_NAME \
    --exclude=$APP_DIR/venv \
    --exclude=$APP_DIR/__pycache__ \
    --exclude=$APP_DIR/.git \
    --exclude=$APP_DIR/output/*.html \
    --exclude=$APP_DIR/output/images \
    $APP_DIR

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backup created successfully: $BACKUP_NAME${NC}"
    
    # Get backup size
    BACKUP_SIZE=$(du -h $BACKUP_DIR/$BACKUP_NAME | cut -f1)
    echo -e "${GREEN}Backup size: $BACKUP_SIZE${NC}"
    
    # Keep only last 7 days of backups
    echo -e "${YELLOW}Cleaning old backups...${NC}"
    find $BACKUP_DIR -name "auto-content-generator_*.tar.gz" -mtime +7 -delete
    
    # Start the application
    echo -e "${YELLOW}Starting application...${NC}"
    systemctl start auto-content-generator
    
    # Check if application started successfully
    sleep 10
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}Application started successfully${NC}"
    else
        echo -e "${RED}Warning: Application may not have started properly${NC}"
    fi
    
else
    echo -e "${RED}Backup failed!${NC}"
    systemctl start auto-content-generator
    exit 1
fi

echo -e "${GREEN}Backup completed successfully!${NC}"