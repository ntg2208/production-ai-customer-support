# UKConnect AI Customer Support - Deployment Guide

## 🚀 Overview
This guide covers deployment strategies for the UKConnect AI Customer Support system across different environments, from local development to enterprise production.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB available space
- **Network**: Stable internet connection for API calls

### API Requirements
- **Google AI API Key**: Required for LLM functionality
- **Database Access**: SQLite (dev) or PostgreSQL (prod)

## 🏠 Local Development Deployment

### Quick Setup
```bash
# Clone repository
git clone https://github.com/ntg2208/production-ai-customer-support
cd production-ai-customer-support

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add your GOOGLE_API_KEY

# Initialize database
python -c "from utils.create_schema import create_database_schema; create_database_schema()"
python -c "from utils.populate_data import populate_data; populate_data()"

# Test deployment
python run_test_scenarios.py
```

### Development Server
```bash
# Interactive testing
python interactive_test.py

# Specific scenario testing
python run_test_scenarios.py --session 1
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize database on container start
RUN python -c "from utils.create_schema import create_database_schema; create_database_schema()"
RUN python -c "from utils.populate_data import populate_data; populate_data()"

# Expose port for web interface (if implemented)
EXPOSE 8000

# Start application
CMD ["python", "interactive_test.py"]
```

### Build and Run
```bash
# Build image
docker build -t ukconnect-support .

# Run container
docker run -e GOOGLE_API_KEY=your_key_here ukconnect-support

# Run with volume mounting for persistence
docker run -v $(pwd)/database:/app/database -e GOOGLE_API_KEY=your_key_here ukconnect-support
```

### Docker Compose
```yaml
version: '3.8'
services:
  ukconnect-app:
    build: .
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/ukconnect
    depends_on:
      - db
    volumes:
      - ./database:/app/database

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=ukconnect
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## ☁️ Cloud Deployment

### Google Cloud Platform

#### Vertex AI Deployment
```bash
# Setup GCP project
gcloud config set project your-project-id

# Deploy to Cloud Run
gcloud run deploy ukconnect-support \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=your_key
```

#### App Engine Deployment
```yaml
# app.yaml
runtime: python38

env_variables:
  GOOGLE_API_KEY: your_key_here
  DATABASE_URL: postgresql://user:pass@host/db

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

### AWS Deployment

#### ECS Deployment
```json
{
  "family": "ukconnect-support",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "ukconnect-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ukconnect:latest",
      "environment": [
        {"name": "GOOGLE_API_KEY", "value": "your_key"},
        {"name": "DATABASE_URL", "value": "postgresql://..."}
      ]
    }
  ]
}
```

#### Lambda Deployment
```bash
# Package for Lambda
zip -r deployment.zip . -x "*.git*" "*__pycache__*"

# Deploy using AWS CLI
aws lambda create-function \
  --function-name ukconnect-support \
  --runtime python3.8 \
  --zip-file fileb://deployment.zip \
  --handler lambda_handler.handler
```

### Azure Deployment

#### Container Instances
```bash
az container create \
  --resource-group ukconnect-rg \
  --name ukconnect-support \
  --image ukconnect:latest \
  --environment-variables GOOGLE_API_KEY=your_key
```

## 🏢 Enterprise Production Deployment

### Infrastructure Requirements

#### Compute Resources
- **CPU**: 4+ cores recommended
- **Memory**: 16GB+ for high throughput
- **Storage**: SSD with 100GB+ space
- **Network**: Load balancer with SSL termination

#### Database Configuration
```sql
-- PostgreSQL production setup
CREATE DATABASE ukconnect_production;
CREATE USER ukconnect_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ukconnect_production TO ukconnect_user;

-- Connection pooling recommended
-- Use PgBouncer or similar
```

### High Availability Setup

#### Load Balancer Configuration
```nginx
# nginx.conf
upstream ukconnect_backend {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 443 ssl;
    server_name support.ukconnect.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://ukconnect_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Auto-scaling Configuration
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ukconnect-support
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ukconnect-support
  template:
    metadata:
      labels:
        app: ukconnect-support
    spec:
      containers:
      - name: ukconnect-app
        image: ukconnect:latest
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: ukconnect-service
spec:
  selector:
    app: ukconnect-support
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔒 Security Configuration

### Environment Variables
```bash
# Production environment variables
export ENVIRONMENT=production
export DEBUG=False
export GOOGLE_API_KEY="secure_api_key"
export DATABASE_URL="postgresql://user:pass@secure-host:5432/ukconnect"
export SECRET_KEY="random_secure_key_for_sessions"
export ALLOWED_HOSTS="support.ukconnect.com,*.ukconnect.com"
```

### SSL/TLS Configuration
```bash
# Generate SSL certificates
certbot --nginx -d support.ukconnect.com

# Auto-renewal
echo "0 0 * * * certbot renew --quiet" | crontab -
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# monitoring.py
import logging
from datetime import datetime

def setup_monitoring():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/var/log/ukconnect/app.log'),
            logging.StreamHandler()
        ]
    )

def track_metrics():
    return {
        "timestamp": datetime.now().isoformat(),
        "response_time": measure_response_time(),
        "active_sessions": count_active_sessions(),
        "error_rate": calculate_error_rate(),
        "memory_usage": get_memory_usage()
    }
```

### Health Checks
```python
# health.py
def health_check():
    try:
        # Test database connectivity
        db = DatabaseManager()
        db.execute("SELECT 1")
        
        # Test API connectivity
        test_api_call()
        
        return {"status": "healthy", "timestamp": datetime.now()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🚀 Performance Optimization

### Caching Strategy
```python
# caching.py
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(key, response, ttl=300):
    redis_client.setex(key, ttl, response)

def get_cached_response(key):
    return redis_client.get(key)
```

### Database Optimization
```sql
-- Index optimization
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
CREATE INDEX idx_bookings_status ON bookings(status);

-- Connection pooling
-- Configure in production settings
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600
}
```

## 📈 Scaling Strategies

### Horizontal Scaling
- **Stateless Design**: Agents can be scaled independently
- **Load Distribution**: Use load balancers to distribute traffic
- **Database Scaling**: Read replicas for query optimization

### Vertical Scaling
- **Memory Optimization**: Increase RAM for better performance
- **CPU Upgrade**: More cores for concurrent processing
- **Storage Enhancement**: SSD for faster database operations

## 🔧 Troubleshooting

### Common Issues

#### API Rate Limits
```python
# Rate limiting handling
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_api_with_retry(prompt):
    try:
        return api_client.generate(prompt)
    except RateLimitError:
        time.sleep(60)  # Wait for rate limit reset
        raise
```

#### Database Connection Issues
```python
# Connection retry logic
def get_db_connection():
    for attempt in range(3):
        try:
            return DatabaseManager()
        except ConnectionError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
```

#### Memory Management
```python
# Memory optimization
import gc

def cleanup_resources():
    gc.collect()  # Force garbage collection
    # Clear caches if needed
    clear_application_cache()
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database schema updated
- [ ] SSL certificates installed
- [ ] Monitoring setup complete
- [ ] Backup strategy implemented

### Post-deployment
- [ ] Health checks passing
- [ ] Performance metrics baseline established
- [ ] Error monitoring active
- [ ] User acceptance testing completed
- [ ] Documentation updated

### Rollback Plan
```bash
# Quick rollback procedure
# 1. Stop current deployment
docker stop ukconnect-support

# 2. Revert to previous version
docker run ukconnect:previous-version

# 3. Verify functionality
curl -f http://localhost:8000/health

# 4. Update load balancer if needed
```

This deployment guide provides comprehensive coverage for deploying the UKConnect AI Customer Support system across various environments and scales.