# FastAPI Deployment & Scalability

## Docker Containerization

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Build (Production)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Development

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: myregistry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Definition

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: LoadBalancer
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### ConfigMap for Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
data:
  app_name: "My FastAPI App"
  log_level: "INFO"
  cors_origins: "https://app.example.com,https://admin.example.com"
```

### Secret for Sensitive Data

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  url: "postgresql://user:password@db-host:5432/mydb"
  secret_key: "your-jwt-secret-key"
```

## Production Server Configuration

### Uvicorn with Gunicorn (Multi-worker)

```bash
# Install
pip install gunicorn uvicorn[standard]

# Run with 4 worker processes
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info \
  --access-logfile - \
  --error-logfile -
```

### Calculate Optimal Workers

```python
import multiprocessing

# Formula: (2 x CPU cores) + 1
workers = (2 * multiprocessing.cpu_count()) + 1
```

### Uvicorn Standalone (Async)

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --log-level info \
  --access-log \
  --use-colors
```

## Scalability Strategies

### 1. Async Everything

```python
# Use async for I/O operations
@app.get("/users/")
async def get_users():
    users = await fetch_users_from_db()  # Non-blocking
    return users
```

### 2. Connection Pooling

```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Connections to maintain
    max_overflow=10,        # Additional connections allowed
    pool_timeout=30,        # Timeout for getting connection
    pool_recycle=3600,      # Recycle after 1 hour
    pool_pre_ping=True,     # Verify connections before use
)
```

### 3. Caching with Redis

```python
from redis import asyncio as aioredis
from functools import wraps
import json

redis = aioredis.from_url("redis://localhost")

def cache(expire: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache first
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await redis.setex(cache_key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/expensive/")
@cache(expire=600)
async def expensive_operation():
    # Expensive computation
    return {"result": "data"}
```

### 4. Background Tasks for Async Processing

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Long-running task
    time.sleep(5)
    print(f"Email sent to {email}")

@app.post("/users/")
async def create_user(user: User, background_tasks: BackgroundTasks):
    # Save user (fast)
    save_user_to_db(user)

    # Send welcome email (slow, runs in background)
    background_tasks.add_task(send_email, user.email, "Welcome!")

    return {"status": "User created"}
```

### 5. Database Query Optimization

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Eager loading to prevent N+1 queries
@app.get("/users-with-items/")
def get_users_with_items(session: SessionDep):
    statement = select(User).options(selectinload(User.items))
    users = session.exec(statement).all()
    return users
```

## Performance Monitoring

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check(session: SessionDep):
    # Check database connection
    try:
        session.exec(select(User).limit(1))
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="Database not available")
```

### Prometheus Metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add metrics endpoint
Instrumentator().instrument(app).expose(app)

# Metrics available at /metrics
```

### Custom Middleware for Timing

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Deployment Checklist

### Pre-deployment

- [ ] Set all secrets via environment variables
- [ ] Configure database migrations (Alembic)
- [ ] Set up logging (structured JSON logs)
- [ ] Configure CORS for production domains
- [ ] Enable HTTPS redirect
- [ ] Set up rate limiting
- [ ] Configure health check endpoints

### Kubernetes Deployment

- [ ] Create Deployment with 3+ replicas
- [ ] Configure HPA for auto-scaling
- [ ] Set resource limits (CPU/memory)
- [ ] Add liveness and readiness probes
- [ ] Use ConfigMaps for configuration
- [ ] Use Secrets for sensitive data
- [ ] Set up Ingress for external access

### Monitoring & Observability

- [ ] Enable Prometheus metrics
- [ ] Set up Grafana dashboards
- [ ] Configure log aggregation (ELK/Loki)
- [ ] Set up alerting (PagerDuty/Slack)
- [ ] Enable distributed tracing (Jaeger)

### Security

- [ ] HTTPS only
- [ ] Strong JWT secret keys
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] SQL injection prevention (use ORM)
- [ ] Input validation on all endpoints

## Platform-Specific Guides

### Vercel Deployment

```python
# vercel.json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### AWS ECS/Fargate

```yaml
# task-definition.json
{
  "family": "fastapi-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "fastapi",
      "image": "myregistry/fastapi:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        }
      ]
    }
  ]
}
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy fastapi-app \
  --image gcr.io/myproject/fastapi:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://..."
```
