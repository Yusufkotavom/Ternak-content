# ⚡ Performance Guide - Auto Content Generator

## Performance Overview

This document outlines performance optimization strategies, monitoring techniques, and best practices for the Auto Content Generator application.

## Performance Metrics

### Key Metrics to Monitor

- **Response Time**: < 2 seconds for API calls
- **Throughput**: > 100 requests/minute
- **Error Rate**: < 1%
- **Resource Usage**: CPU < 80%, Memory < 85%
- **Concurrent Users**: > 50 simultaneous users

## Performance Optimization

### 1. Caching Strategy

```python
import redis
import json
from functools import wraps
from typing import Any, Optional

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
    
    def cache_result(self, expire_time: int = 3600):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                self.redis.setex(cache_key, expire_time, json.dumps(result))
                return result
            return wrapper
        return decorator

# Usage
cache_manager = CacheManager()

@cache_manager.cache_result(expire_time=1800)  # 30 minutes
async def research_keyword(keyword: str) -> dict:
    # Expensive keyword research operation
    pass
```

### 2. Database Optimization

```python
from sqlalchemy import create_engine, Index
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Optimized database configuration
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Disable SQL logging in production
)

# Create indexes for better performance
Index('idx_keyword_created', Content.keyword, Content.created_at)
Index('idx_status_created', Content.status, Content.created_at)
```

### 3. Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

class AsyncProcessor:
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_bulk_keywords(self, keywords: List[str]) -> List[dict]:
        """Process multiple keywords concurrently"""
        tasks = []
        for keyword in keywords:
            task = asyncio.create_task(self.process_single_keyword(keyword))
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def process_single_keyword(self, keyword: str) -> dict:
        """Process single keyword with all steps"""
        # Run CPU-intensive tasks in thread pool
        loop = asyncio.get_event_loop()
        
        # Research
        research_task = loop.run_in_executor(
            self.executor, 
            self._research_keyword_sync, 
            keyword
        )
        
        # Generate content
        content_task = loop.run_in_executor(
            self.executor,
            self._generate_content_sync,
            keyword
        )
        
        # Wait for both tasks
        research_result, content_result = await asyncio.gather(
            research_task, content_task
        )
        
        return {
            "keyword": keyword,
            "research": research_result,
            "content": content_result
        }
```

### 4. Memory Optimization

```python
import gc
from typing import Generator

class MemoryOptimizer:
    def __init__(self):
        self.large_objects = []
    
    def process_large_dataset(self, data: List[dict]) -> Generator[dict, None, None]:
        """Process large datasets in chunks to avoid memory issues"""
        chunk_size = 1000
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            
            # Process chunk
            for item in chunk:
                yield self.process_item(item)
            
            # Force garbage collection
            gc.collect()
    
    def optimize_image_processing(self, images: List[str]) -> List[str]:
        """Optimize image processing to reduce memory usage"""
        optimized_images = []
        
        for image_path in images:
            # Process image in smaller chunks
            with Image.open(image_path) as img:
                # Resize to reduce memory usage
                if img.size[0] > 1920 or img.size[1] > 1080:
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                
                # Save optimized version
                optimized_path = image_path.replace('.jpg', '_optimized.jpg')
                img.save(optimized_path, 'JPEG', quality=85, optimize=True)
                optimized_images.append(optimized_path)
        
        return optimized_images
```

### 5. API Rate Limiting

```python
import time
from collections import defaultdict
from fastapi import HTTPException

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
    
    def check_rate_limit(self, client_id: str):
        if not self.is_allowed(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

# Usage in FastAPI
rate_limiter = RateLimiter(max_requests=100, window=3600)

@app.post("/api/process-keywords")
async def process_keywords(request: Request, data: KeywordRequest):
    client_id = request.client.host
    rate_limiter.check_rate_limit(client_id)
    
    # Process request
    return await process_keywords_data(data)
```

## Monitoring & Profiling

### 1. Performance Monitoring

```python
import time
import psutil
import logging
from functools import wraps

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def monitor_performance(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                end_memory = psutil.Process().memory_info().rss
                memory_used = end_memory - start_memory
                
                self.logger.info(f"{func.__name__} completed in {execution_time:.2f}s, memory: {memory_used/1024/1024:.2f}MB")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
                raise
        return wrapper

# Usage
monitor = PerformanceMonitor()

@monitor.monitor_performance
async def generate_content(keyword: str) -> dict:
    # Content generation logic
    pass
```

### 2. Resource Monitoring

```python
import psutil
import asyncio
from datetime import datetime

class ResourceMonitor:
    def __init__(self):
        self.metrics = []
    
    async def monitor_resources(self):
        """Monitor system resources continuously"""
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metric = {
                "timestamp": datetime.utcnow(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free
            }
            
            self.metrics.append(metric)
            
            # Keep only last 1000 metrics
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
            
            # Alert if thresholds exceeded
            if cpu_percent > 80:
                self.send_alert("High CPU usage", metric)
            
            if memory.percent > 85:
                self.send_alert("High memory usage", metric)
            
            await asyncio.sleep(60)  # Check every minute
    
    def send_alert(self, message: str, metric: dict):
        # Send alert to monitoring system
        print(f"ALERT: {message} - {metric}")
```

### 3. Profiling Tools

```python
import cProfile
import pstats
import io
from functools import wraps

def profile_function(func):
    """Profile function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # Save profiling stats
            s = io.StringIO()
            stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            stats.print_stats()
            
            # Log profiling results
            with open(f"profile_{func.__name__}.txt", "w") as f:
                f.write(s.getvalue())

# Usage
@profile_function
async def expensive_operation():
    # Expensive operation
    pass
```

## Database Performance

### 1. Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Optimized connection pool
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=20,           # Number of connections to maintain
    max_overflow=30,        # Additional connections when pool is full
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False              # Disable SQL logging
)
```

### 2. Query Optimization

```python
from sqlalchemy.orm import joinedload, selectinload

# Optimize queries with eager loading
def get_content_with_relations(content_id: int):
    return session.query(Content)\
        .options(
            joinedload(Content.images),
            selectinload(Content.tags)
        )\
        .filter(Content.id == content_id)\
        .first()

# Use bulk operations for large datasets
def bulk_insert_contents(contents: List[dict]):
    session.bulk_insert_mappings(Content, contents)
    session.commit()
```

## Caching Strategies

### 1. Multi-Level Caching

```python
import redis
from functools import lru_cache

class MultiLevelCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.local_cache = {}
    
    @lru_cache(maxsize=1000)
    def get_from_local_cache(self, key: str):
        """Level 1: Local memory cache"""
        return self.local_cache.get(key)
    
    def get_from_redis_cache(self, key: str):
        """Level 2: Redis cache"""
        return self.redis.get(key)
    
    def get_cached_data(self, key: str):
        # Try local cache first
        result = self.get_from_local_cache(key)
        if result:
            return result
        
        # Try Redis cache
        result = self.get_from_redis_cache(key)
        if result:
            # Store in local cache
            self.local_cache[key] = result
            return result
        
        return None
```

### 2. Cache Invalidation

```python
class CacheInvalidator:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def invalidate_keyword_cache(self, keyword: str):
        """Invalidate cache for specific keyword"""
        patterns = [
            f"research_keyword:{keyword}",
            f"generate_content:{keyword}",
            f"generate_images:{keyword}"
        ]
        
        for pattern in patterns:
            self.invalidate_pattern(pattern)
```

## Load Balancing

### 1. Application Load Balancing

```python
import random
from typing import List

class LoadBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.current_index = 0
    
    def get_next_server(self) -> str:
        """Round-robin load balancing"""
        server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return server
    
    def get_random_server(self) -> str:
        """Random load balancing"""
        return random.choice(self.servers)
    
    def get_least_loaded_server(self) -> str:
        """Least loaded server (requires health checks)"""
        # Implementation would check server health
        return self.get_next_server()

# Usage
load_balancer = LoadBalancer([
    "http://server1:8000",
    "http://server2:8000",
    "http://server3:8000"
])
```

### 2. Database Load Balancing

```python
class DatabaseLoadBalancer:
    def __init__(self, primary_db: str, replica_dbs: List[str]):
        self.primary_db = primary_db
        self.replica_dbs = replica_dbs
    
    def get_read_connection(self):
        """Get connection for read operations (use replica)"""
        return random.choice(self.replica_dbs)
    
    def get_write_connection(self):
        """Get connection for write operations (use primary)"""
        return self.primary_db
```

## Performance Testing

### 1. Load Testing

```python
import asyncio
import aiohttp
import time
from typing import List

class LoadTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def test_endpoint(self, endpoint: str, requests: int, concurrent: int):
        """Test endpoint with specified load"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            start_time = time.time()
            
            for i in range(requests):
                task = asyncio.create_task(
                    self.make_request(session, endpoint)
                )
                tasks.append(task)
                
                # Limit concurrent requests
                if len(tasks) >= concurrent:
                    await asyncio.gather(*tasks)
                    tasks = []
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"Completed {requests} requests in {total_time:.2f}s")
            print(f"Average response time: {total_time/requests:.2f}s")
            print(f"Requests per second: {requests/total_time:.2f}")
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str):
        """Make single request"""
        start_time = time.time()
        
        async with session.post(f"{self.base_url}{endpoint}", json={
            "keywords": ["test keyword"]
        }) as response:
            response_time = time.time() - start_time
            return response.status, response_time

# Usage
load_tester = LoadTester("http://localhost:8000")
asyncio.run(load_tester.test_endpoint("/process-keywords", 1000, 50))
```

### 2. Stress Testing

```python
class StressTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def stress_test(self, max_concurrent: int = 100):
        """Stress test the application"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Create maximum concurrent requests
            for i in range(max_concurrent):
                task = asyncio.create_task(
                    self.make_stress_request(session, i)
                )
                tasks.append(task)
            
            # Execute all requests simultaneously
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successful = sum(1 for r in results if isinstance(r, tuple) and r[0] == 200)
            failed = len(results) - successful
            
            print(f"Stress test completed:")
            print(f"Successful requests: {successful}")
            print(f"Failed requests: {failed}")
            print(f"Success rate: {successful/len(results)*100:.2f}%")
    
    async def make_stress_request(self, session: aiohttp.ClientSession, request_id: int):
        """Make stress test request"""
        try:
            async with session.post(f"{self.base_url}/process-keywords", json={
                "keywords": [f"stress_test_keyword_{request_id}"]
            }, timeout=aiohttp.ClientTimeout(total=30)) as response:
                return response.status, await response.text()
        except Exception as e:
            return f"Error: {str(e)}"
```

## Performance Checklist

### Pre-Deployment

- [ ] Caching implemented for expensive operations
- [ ] Database queries optimized with proper indexes
- [ ] Connection pooling configured
- [ ] Rate limiting implemented
- [ ] Monitoring and alerting set up
- [ ] Load testing completed

### Post-Deployment

- [ ] Performance metrics being collected
- [ ] Response times within acceptable limits
- [ ] Resource usage monitored
- [ ] Error rates tracked
- [ ] Scaling plan ready

### Ongoing Optimization

- [ ] Regular performance reviews
- [ ] Cache hit rates monitored
- [ ] Database query performance analyzed
- [ ] New bottlenecks identified and resolved
- [ ] Performance improvements implemented

---

**Remember: Performance optimization is an iterative process! ⚡**