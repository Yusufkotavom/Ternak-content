#!/bin/bash

# Auto Content Generator Monitoring Script

# Configuration
APP_URL="http://localhost:8000"
LOG_FILE="/var/log/auto-content-generator/monitor.log"
ALERT_EMAIL="admin@yourdomain.com"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
    echo -e "$1"
}

# Function to send email alert
send_email_alert() {
    local subject="$1"
    local message="$2"
    
    echo "$message" | mail -s "$subject" $ALERT_EMAIL
    log_message "${RED}Email alert sent: $subject${NC}"
}

# Function to send Slack alert
send_slack_alert() {
    local message="$1"
    
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$message\"}" \
        $SLACK_WEBHOOK
    log_message "${RED}Slack alert sent: $message${NC}"
}

# Function to check application health
check_health() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" $APP_URL/health)
    
    if [ "$response" = "200" ]; then
        log_message "${GREEN}✓ Application is healthy (HTTP $response)${NC}"
        return 0
    else
        log_message "${RED}✗ Application health check failed (HTTP $response)${NC}"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 90 ]; then
        log_message "${RED}✗ Disk space critical: ${usage}% used${NC}"
        send_email_alert "Disk Space Alert" "Disk usage is at ${usage}%"
        send_slack_alert "🚨 Disk space critical: ${usage}% used"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log_message "${YELLOW}⚠ Disk space warning: ${usage}% used${NC}"
        return 0
    else
        log_message "${GREEN}✓ Disk space OK: ${usage}% used${NC}"
        return 0
    fi
}

# Function to check memory usage
check_memory() {
    local usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    if [ "$usage" -gt 90 ]; then
        log_message "${RED}✗ Memory usage critical: ${usage}%${NC}"
        send_email_alert "Memory Alert" "Memory usage is at ${usage}%"
        send_slack_alert "🚨 Memory usage critical: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log_message "${YELLOW}⚠ Memory usage warning: ${usage}%${NC}"
        return 0
    else
        log_message "${GREEN}✓ Memory usage OK: ${usage}%${NC}"
        return 0
    fi
}

# Function to check service status
check_service() {
    if systemctl is-active --quiet auto-content-generator; then
        log_message "${GREEN}✓ Service is running${NC}"
        return 0
    else
        log_message "${RED}✗ Service is not running${NC}"
        send_email_alert "Service Alert" "Auto Content Generator service is down"
        send_slack_alert "🚨 Auto Content Generator service is down"
        return 1
    fi
}

# Function to check recent errors in logs
check_logs() {
    local error_count=$(journalctl -u auto-content-generator --since "10 minutes ago" | grep -i error | wc -l)
    
    if [ "$error_count" -gt 10 ]; then
        log_message "${RED}✗ High error count in logs: $error_count errors in last 10 minutes${NC}"
        send_email_alert "Log Alert" "High error count: $error_count errors in last 10 minutes"
        send_slack_alert "🚨 High error count: $error_count errors in last 10 minutes"
        return 1
    elif [ "$error_count" -gt 5 ]; then
        log_message "${YELLOW}⚠ Moderate error count: $error_count errors in last 10 minutes${NC}"
        return 0
    else
        log_message "${GREEN}✓ Log errors OK: $error_count errors in last 10 minutes${NC}"
        return 0
    fi
}

# Function to check API response time
check_response_time() {
    local start_time=$(date +%s.%N)
    local response=$(curl -s -o /dev/null -w "%{http_code}" $APP_URL/health)
    local end_time=$(date +%s.%N)
    local response_time=$(echo "$end_time - $start_time" | bc)
    
    if (( $(echo "$response_time > 5.0" | bc -l) )); then
        log_message "${RED}✗ Slow response time: ${response_time}s${NC}"
        send_email_alert "Performance Alert" "Slow response time: ${response_time}s"
        send_slack_alert "🐌 Slow response time: ${response_time}s"
        return 1
    elif (( $(echo "$response_time > 2.0" | bc -l) )); then
        log_message "${YELLOW}⚠ Moderate response time: ${response_time}s${NC}"
        return 0
    else
        log_message "${GREEN}✓ Response time OK: ${response_time}s${NC}"
        return 0
    fi
}

# Main monitoring function
main() {
    log_message "${GREEN}Starting monitoring check...${NC}"
    
    local overall_status=0
    
    # Run all checks
    check_health || overall_status=1
    check_disk_space || overall_status=1
    check_memory || overall_status=1
    check_service || overall_status=1
    check_logs || overall_status=1
    check_response_time || overall_status=1
    
    # Summary
    if [ $overall_status -eq 0 ]; then
        log_message "${GREEN}✓ All checks passed${NC}"
    else
        log_message "${RED}✗ Some checks failed${NC}"
        send_email_alert "Monitoring Alert" "Some system checks failed. Check logs for details."
        send_slack_alert "⚠️ Some system checks failed"
    fi
    
    log_message "${GREEN}Monitoring check completed${NC}"
    echo "----------------------------------------"
}

# Run main function
main