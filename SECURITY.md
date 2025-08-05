# 🔒 Security Guide - Auto Content Generator

## Security Overview

This document outlines security best practices, vulnerabilities to watch for, and how to secure the Auto Content Generator application.

## Security Checklist

### ✅ Environment Security

- [ ] API keys stored in environment variables, not in code
- [ ] `.env` file excluded from version control
- [ ] Production secrets not committed to repository
- [ ] Database credentials encrypted
- [ ] SSL/TLS certificates properly configured

### ✅ Application Security

- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] CSRF protection implemented
- [ ] Rate limiting configured
- [ ] Authentication/authorization in place

### ✅ Infrastructure Security

- [ ] Firewall rules configured
- [ ] SSH key-based authentication
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Monitoring and alerting

## Security Vulnerabilities

### 1. API Key Exposure

**Risk**: High
**Mitigation**:
```bash
# Never commit API keys
echo "OPENAI_API_KEY=sk-..." >> .gitignore

# Use environment variables
export OPENAI_API_KEY="your-key-here"

# Rotate keys regularly
# Monitor API usage for anomalies
```

### 2. Input Validation

**Risk**: Medium
**Mitigation**:
```python
# Validate input data
from pydantic import BaseModel, validator

class KeywordRequest(BaseModel):
    keywords: List[str]
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if not v:
            raise ValueError('Keywords cannot be empty')
        if len(v) > 100:
            raise ValueError('Too many keywords')
        return v
```

### 3. File Upload Security

**Risk**: High
**Mitigation**:
```python
# Validate file uploads
ALLOWED_EXTENSIONS = {'.csv', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile):
    if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
        raise HTTPException(400, "Invalid file type")
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
```

### 4. SQL Injection

**Risk**: High
**Mitigation**:
```python
# Use parameterized queries
# Never use string formatting for SQL
import sqlalchemy

# Good
query = session.query(User).filter(User.id == user_id)

# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"
```

### 5. XSS Protection

**Risk**: Medium
**Mitigation**:
```python
# Sanitize HTML output
import html

def sanitize_html(content: str) -> str:
    return html.escape(content)

# Use Jinja2 auto-escape
app = FastAPI()
templates = Jinja2Templates(directory="templates")
templates.env.auto_escape = True
```

## Security Headers

### Nginx Configuration

```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### FastAPI Security

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

## Authentication & Authorization

### 1. API Key Authentication

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = credentials.credentials
    if not is_valid_api_key(api_key):
        raise HTTPException(401, "Invalid API key")
    return api_key

@app.post("/secure-endpoint")
async def secure_endpoint(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### 2. Rate Limiting

```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        client_requests[:] = [req for req in client_requests if now - req < self.window]
        
        if len(client_requests) >= self.max_requests:
            return False
        
        client_requests.append(now)
        return True
```

## Data Protection

### 1. Encryption at Rest

```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(base64.urlsafe_b64encode(key.encode()))
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### 2. Secure File Storage

```python
import os
from pathlib import Path

class SecureFileStorage:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, filename: str, content: bytes) -> str:
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)
        file_path = self.base_path / safe_filename
        
        # Save with restricted permissions
        with open(file_path, 'wb') as f:
            f.write(content)
        
        os.chmod(file_path, 0o600)  # Read/write for owner only
        return str(file_path)
    
    def _sanitize_filename(self, filename: str) -> str:
        # Remove dangerous characters
        return "".join(c for c in filename if c.isalnum() or c in "._-")
```

## Logging & Monitoring

### 1. Security Event Logging

```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_security_event(self, event_type: str, details: dict):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": "high" if event_type in ["auth_failure", "injection_attempt"] else "medium"
        }
        self.logger.warning(json.dumps(log_entry))
```

### 2. Intrusion Detection

```python
class IntrusionDetector:
    def __init__(self):
        self.suspicious_patterns = [
            r"<script>",
            r"javascript:",
            r"union.*select",
            r"drop.*table",
            r"exec.*sp_",
        ]
    
    def detect_suspicious_activity(self, input_data: str) -> bool:
        import re
        for pattern in self.suspicious_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
        return False
```

## Network Security

### 1. Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/TLS Configuration

```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

## Backup Security

### 1. Encrypted Backups

```bash
#!/bin/bash
# Encrypted backup script

BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# Create backup
tar -czf $BACKUP_FILE /opt/auto-content-generator

# Encrypt backup
gpg --encrypt --recipient your-email@domain.com $BACKUP_FILE

# Remove unencrypted backup
rm $BACKUP_FILE

# Upload to secure storage
aws s3 cp $ENCRYPTED_FILE s3://your-backup-bucket/
```

### 2. Backup Verification

```python
import hashlib
import os

class BackupVerifier:
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
    
    def verify_backup(self) -> bool:
        # Check file integrity
        if not os.path.exists(self.backup_path):
            return False
        
        # Verify checksum
        expected_checksum = self._get_expected_checksum()
        actual_checksum = self._calculate_checksum()
        
        return expected_checksum == actual_checksum
    
    def _calculate_checksum(self) -> str:
        with open(self.backup_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
```

## Incident Response

### 1. Security Incident Plan

```python
class SecurityIncidentHandler:
    def __init__(self):
        self.incident_log = []
    
    def handle_incident(self, incident_type: str, details: dict):
        # Log incident
        self.incident_log.append({
            "timestamp": datetime.utcnow(),
            "type": incident_type,
            "details": details
        })
        
        # Take immediate action
        if incident_type == "api_key_exposure":
            self._rotate_api_keys()
        elif incident_type == "suspicious_activity":
            self._block_ip(details.get("ip_address"))
        
        # Notify administrators
        self._send_alert(incident_type, details)
    
    def _rotate_api_keys(self):
        # Implement API key rotation
        pass
    
    def _block_ip(self, ip_address: str):
        # Implement IP blocking
        pass
    
    def _send_alert(self, incident_type: str, details: dict):
        # Send alert to administrators
        pass
```

### 2. Recovery Procedures

```bash
#!/bin/bash
# Security incident recovery script

echo "Starting security incident recovery..."

# 1. Isolate affected systems
systemctl stop auto-content-generator

# 2. Backup current state
tar -czf incident_backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/auto-content-generator

# 3. Rotate credentials
# Update API keys, database passwords, etc.

# 4. Restore from clean backup
./scripts/restore.sh clean_backup.tar.gz

# 5. Verify system integrity
python test_system.py

# 6. Restart services
systemctl start auto-content-generator

echo "Recovery completed"
```

## Security Testing

### 1. Vulnerability Scanning

```bash
# Run security scans
nmap -sV -sC your-server.com
nikto -h your-server.com
sqlmap -u "http://your-server.com/api/endpoint"
```

### 2. Penetration Testing

```python
# Security test suite
import pytest
from fastapi.testclient import TestClient

class SecurityTests:
    def test_sql_injection(self, client: TestClient):
        # Test for SQL injection vulnerabilities
        response = client.post("/api/endpoint", json={
            "input": "'; DROP TABLE users; --"
        })
        assert response.status_code == 400
    
    def test_xss_protection(self, client: TestClient):
        # Test for XSS vulnerabilities
        response = client.post("/api/endpoint", json={
            "input": "<script>alert('xss')</script>"
        })
        # Verify input is sanitized
        assert "<script>" not in response.text
    
    def test_authentication(self, client: TestClient):
        # Test authentication requirements
        response = client.get("/api/secure-endpoint")
        assert response.status_code == 401
```

## Compliance

### 1. GDPR Compliance

```python
class GDPRCompliance:
    def __init__(self):
        self.data_retention_days = 30
    
    def anonymize_user_data(self, user_data: dict) -> dict:
        # Remove personally identifiable information
        anonymized = user_data.copy()
        anonymized.pop('email', None)
        anonymized.pop('ip_address', None)
        anonymized.pop('user_agent', None)
        return anonymized
    
    def delete_user_data(self, user_id: str):
        # Implement right to be forgotten
        pass
    
    def export_user_data(self, user_id: str) -> dict:
        # Implement data portability
        pass
```

### 2. Data Retention Policy

```python
class DataRetention:
    def __init__(self):
        self.retention_policies = {
            "logs": 90,  # days
            "backups": 365,  # days
            "user_data": 30,  # days
        }
    
    def cleanup_expired_data(self):
        # Remove data older than retention period
        pass
```

## Security Checklist for Deployment

### Pre-Deployment

- [ ] All API keys rotated
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Monitoring set up

### Post-Deployment

- [ ] Security scan completed
- [ ] Penetration test passed
- [ ] Backup system tested
- [ ] Incident response plan ready
- [ ] Team trained on security procedures

---

**Remember: Security is an ongoing process, not a one-time setup! 🔒**