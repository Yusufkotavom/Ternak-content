# 🛠️ Development Guide - Auto Content Generator

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional)
- VS Code (recommended)

### Local Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/auto-content-eeat.git
cd auto-content-eeat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # Create this file for dev tools
```

### Development Dependencies

Create `requirements-dev.txt`:
```
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
```

## Project Structure

```
auto-content-eeat/
├── src/
│   ├── modules/           # Core modules
│   │   ├── keyword_research.py
│   │   ├── content_generator.py
│   │   ├── image_generator.py
│   │   └── wordpress_publisher.py
│   ├── utils/             # Utilities
│   │   └── config.py
│   └── models/            # Data models
├── templates/             # HTML templates
├── static/               # Static files
├── scripts/              # Deployment scripts
├── tests/                # Test files
├── docs/                 # Documentation
└── examples/             # Example files
```

## Development Workflow

### 1. Code Style

```bash
# Format code with Black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### 2. Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_keyword_research.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run async tests
pytest tests/test_async.py -v
```

### 3. Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
```

## Adding New Features

### 1. New Module

```python
# src/modules/new_feature.py
"""
New Feature Module
Description of what this module does
"""

import asyncio
from typing import Dict, List
from src.utils.config import Settings

class NewFeature:
    def __init__(self):
        self.settings = Settings()
    
    async def process_feature(self, data: Dict) -> Dict:
        """Process the new feature"""
        # Implementation here
        pass
```

### 2. Update Main Application

```python
# main.py
from src.modules.new_feature import NewFeature

# Initialize
new_feature = NewFeature()

# Use in endpoint
@app.post("/new-feature")
async def new_feature_endpoint(request: NewFeatureRequest):
    result = await new_feature.process_feature(request.data)
    return result
```

### 3. Add Tests

```python
# tests/test_new_feature.py
import pytest
from src.modules.new_feature import NewFeature

@pytest.mark.asyncio
async def test_new_feature():
    feature = NewFeature()
    result = await feature.process_feature({"test": "data"})
    assert result is not None
```

## API Development

### 1. Adding New Endpoints

```python
# In main.py
@app.post("/api/v1/new-endpoint")
async def new_endpoint(request: NewRequest):
    """New endpoint description"""
    try:
        # Process request
        result = await process_request(request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Request/Response Models

```python
# src/models/api.py
from pydantic import BaseModel
from typing import List, Optional

class NewRequest(BaseModel):
    keyword: str
    options: Optional[Dict] = None

class NewResponse(BaseModel):
    status: str
    data: Dict
    message: Optional[str] = None
```

## Database Integration

### 1. SQLAlchemy Models

```python
# src/models/database.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. Database Operations

```python
# src/modules/database.py
from sqlalchemy.orm import Session
from src.models.database import Content

class DatabaseManager:
    def __init__(self, session: Session):
        self.session = session
    
    async def save_content(self, content_data: Dict) -> Content:
        content = Content(**content_data)
        self.session.add(content)
        self.session.commit()
        return content
```

## Frontend Development

### 1. Adding New UI Components

```html
<!-- templates/new_component.html -->
<div class="new-component">
    <h3>{{ title }}</h3>
    <div class="content">
        {{ content }}
    </div>
</div>
```

### 2. JavaScript Integration

```javascript
// static/js/new-feature.js
async function newFeature() {
    try {
        const response = await fetch('/api/v1/new-endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                keyword: 'test',
                options: {}
            })
        });
        
        const result = await response.json();
        console.log(result);
    } catch (error) {
        console.error('Error:', error);
    }
}
```

## Configuration Management

### 1. Environment Variables

```python
# src/utils/config.py
class Settings(BaseSettings):
    # Add new settings
    new_feature_enabled: bool = True
    new_api_key: Optional[str] = None
    new_api_url: str = "https://api.example.com"
    
    class Config:
        env_file = ".env"
```

### 2. Feature Flags

```python
# src/utils/features.py
class FeatureFlags:
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def is_new_feature_enabled(self) -> bool:
        return self.settings.new_feature_enabled
```

## Testing Strategy

### 1. Unit Tests

```python
# tests/test_modules/test_keyword_research.py
import pytest
from unittest.mock import Mock, patch
from src.modules.keyword_research import KeywordResearch

@pytest.mark.asyncio
async def test_research_keyword():
    research = KeywordResearch()
    
    with patch('src.modules.keyword_research.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}
        
        result = await research.research_keyword("test")
        assert result["keyword"] == "test"
```

### 2. Integration Tests

```python
# tests/test_integration/test_full_pipeline.py
@pytest.mark.asyncio
async def test_full_content_generation():
    # Test complete pipeline
    research = KeywordResearch()
    generator = ContentGenerator()
    
    research_data = await research.research_keyword("test")
    content = await generator.generate_content("test", {}, research_data)
    
    assert content["title"] is not None
    assert content["content"] is not None
```

### 3. API Tests

```python
# tests/test_api/test_endpoints.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Performance Optimization

### 1. Caching

```python
# src/utils/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, expire_time, result)
            return result
        return wrapper
    return decorator
```

### 2. Async Optimization

```python
# Use asyncio.gather for concurrent operations
async def process_multiple_keywords(keywords: List[str]):
    tasks = [process_single_keyword(keyword) for keyword in keywords]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Deployment

### 1. Docker Development

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
```

### 2. Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=True
      - PYTHONPATH=/app
```

## Documentation

### 1. Code Documentation

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Complex function that does something important.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dictionary containing the result
        
    Raises:
        ValueError: If parameters are invalid
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### 2. API Documentation

```python
@app.post("/api/v1/process", response_model=ProcessResponse)
async def process_keywords(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Process keywords and generate content.
    
    This endpoint accepts a list of keywords and generates
    content for each keyword using AI and E-E-A-T principles.
    
    - **keywords**: List of keywords to process
    - **options**: Optional configuration parameters
    
    Returns:
        ProcessResponse: Processing results
    """
    pass
```

## Monitoring and Logging

### 1. Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(self, event_type: str, data: Dict):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.logger.info(json.dumps(log_entry))
```

### 2. Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            print(f"{func.__name__} took {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"{func.__name__} failed after {execution_time:.2f} seconds")
            raise
    return wrapper
```

## Contributing

### 1. Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit changes: `git commit -m "Add new feature"`
7. Push to branch: `git push origin feature/new-feature`
8. Create Pull Request

### 2. Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

---

**Happy Coding! 🚀**