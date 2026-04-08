# MAARS Infinity - Production Deployment Guide

Complete guide for deploying MAARS Infinity to production environments.

## Deployment Architectures

MAARS Infinity supports multiple deployment models:

| Model | Use Case | Complexity | Cost |
|-------|----------|-----------|------|
| **Docker Compose** | Single server, dev/staging | Low | Low |
| **Docker + Kubernetes** | Scalable, multi-region | High | Medium |
| **Cloud Platform** | AWS/GCP/Azure managed | Medium | Medium-High |
| **Serverless** | Microservices, auto-scaling | Very High | Pay-per-use |

## Quick Start - Docker Compose

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Linux/macOS/Windows with Docker Desktop

### Deploy in 5 Minutes

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/MAARS-Command.git
   cd MAARS-Command
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with production values
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Verify Deployment**
   ```bash
   docker-compose logs
   # Should show:
   # backend: Uvicorn running on http://0.0.0.0:8000
   # frontend: Compiled successfully
   ```

5. **Access Application**
   - Frontend: `https://your-domain.com`
   - API Docs: `https://your-domain.com/docs`
   - Health Check: `curl https://your-domain.com/api/health`

## Complete Deployment Process

### Phase 1: Pre-Deployment Checklist

- [ ] **Code Pushed:** All changes committed and pushed to main branch
- [ ] **Tests Pass:** Run `python -m pytest tests/` and `yarn test` locally
- [ ] **Dependencies Updated:** `pip freeze > requirements.txt` and `yarn lock` committed
- [ ] **Secrets Configured:** All environment variables set (never commit .env!)
- [ ] **Database Backed Up:** MongoDB snapshot created
- [ ] **SSL Certificate Ready:** Valid certificate for domain
- [ ] **DNS Configured:** Domain points to deployment server
- [ ] **Monitoring Set Up:** Sentry, logs aggregation, uptime monitoring configured
- [ ] **Rollback Plan:** Know how to revert to previous version

### Phase 2: Environment Preparation

#### Production Environment Variables

Create `.env` with **all** required production values:

```bash
# ==================== REQUIRED ====================
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net
DB_NAME=maars_infinity_prod
JWT_SECRET=your-production-jwt-secret-use-strong-key
ENVIRONMENT=production

# ==================== SERVER ====================
SERVER_PORT=8000
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=500

# ==================== LLM PROVIDERS ====================
# Set at least ONE of these
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# ==================== INTEGRATIONS ====================
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_EMAIL=apikey
SMTP_PASSWORD=SG...
STRIPE_API_KEY=sk_live_...

# ==================== SECURITY ====================
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DEBUG=false

# ==================== MONITORING ====================
LOG_LEVEL=INFO
SENTRY_DSN=https://...@sentry.io/...
```

**Never commit `.env` to version control!** Use:
- GitHub Secrets for CI/CD
- Docker Compose `.env` file (gitignored)
- Environment variable services (AWS Secrets Manager, etc.)

#### Generate Secure JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to JWT_SECRET in .env
```

### Phase 3: Database Setup

#### MongoDB Atlas (Recommended - Managed Service)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create cluster (minimum M5 - general purpose)
3. Enable Network Access (IP whitelist)
4. Create database user with strong password
5. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/db_name`
6. Set `MONGO_URL` in `.env`

**About MongoDB versions:**
- Atlas provides auto-scaling and backups (recommended for production)
- Self-hosted requires manual scaling and backup strategy
- Minimum version: 5.0 (MAARS uses some 5.0+ features)

#### Local MongoDB (Alternative - Not Recommended for Production)

```bash
# Install MongoDB Enterprise Edition
# See: https://docs.mongodb.com/manual/installation/

# Start with authentication
mongod --auth --dbpath /data/db

# Create admin user
mongosh
db.createUser({user: "admin", pwd: "STRONG_PASSWORD", roles: ["root"]})

# Create application user
use maars_infinity
db.createUser({
  user: "app_user",
  pwd: "STRONG_PASSWORD", 
  roles: ["readWrite", "dbAdmin"]
})
```

#### Database Indexes

Backend automatically creates required indexes on startup. Verify:

```bash
mongosh --username user --password pass --authenticationDatabase admin
use maars_infinity
db.getCollectionNames()
db.chats.getIndexes()  # Should show various indexes
```

### Phase 4: Container Setup

#### Build Docker Images

```bash
# Option 1: Use pre-built images from registry
# (if you've pushed to Docker Hub/ECR)
docker pull your-registry/maars-backend:latest
docker pull your-registry/maars-frontend:latest

# Option 2: Build locally
docker build -t maars-backend:latest ./backend
docker build -t maars-frontend:latest ./frontend
```

#### Configure docker-compose.yml

```yaml
version: '3.8'

services:
  mongo:
    image: mongo:6.0
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: mongosh --eval "db.adminCommand('ping')"
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      MONGO_URL: ${MONGO_URL}
      DB_NAME: ${DB_NAME}
      JWT_SECRET: ${JWT_SECRET}
      ENVIRONMENT: ${ENVIRONMENT}
      # ... all other env vars from .env
    depends_on:
      mongo:
        condition: service_healthy
    healthcheck:
      test: curl --fail http://localhost:8000/api/health
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build:
      context: ./frontend
      args:
        REACT_APP_BACKEND_URL: ${REACT_APP_BACKEND_URL}
    restart: always
    ports:
      - "3000:3000"
    depends_on:
      - backend
    healthcheck:
      test: curl --fail http://localhost:3000 || exit 1
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt/:/etc/letsencrypt/:ro
      - ./html:/usr/share/nginx/html:ro
    depends_on:
      - backend
      - frontend

volumes:
  mongo_data:
```

### Phase 5: SSL/TLS Setup

#### Using Let's Encrypt (Recommended - Free)

```bash
# Install Certbot
curl https://get.acme.sh | sh

# Generate certificate (requires domain DNS pointing to server)
acme.sh --issue -d your-domain.com -d www.your-domain.com --webroot ./html

# Copy certificates
mkdir -p /etc/letsencrypt/
cp ~/.acme.sh/your-domain.com/ /etc/letsencrypt/
```

#### Using Existing Certificate

```bash
# Copy to accessible location
cp /path/to/cert.pem /etc/letsencrypt/cert.pem
cp /path/to/key.pem /etc/letsencrypt/key.pem
chmod 644 /etc/letsencrypt/cert.pem
chmod 400 /etc/letsencrypt/key.pem
```

#### Configure Nginx with SSL

Create `nginx.conf`:

```nginx
upstream backend {
  server backend:8000;
}

upstream frontend {
  server frontend:3000;
}

# Redirect HTTP to HTTPS
server {
  listen 80;
  server_name your-domain.com www.your-domain.com;
  return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
  listen 443 ssl http2;
  server_name your-domain.com www.your-domain.com;

  # SSL certificates
  ssl_certificate /etc/letsencrypt/cert.pem;
  ssl_certificate_key /etc/letsencrypt/key.pem;

  # Security headers
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-XSS-Protection "1; mode=block" always;

  # Gzip compression
  gzip on;
  gzip_types text/javascript application/javascript text/css;
  gzip_min_length 1000;

  # Frontend
  location / {
    proxy_pass http://frontend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  # Backend API
  location /api/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
    proxy_request_buffering off;
  }

  # WebSocket support
  location /api/ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

### Phase 6: Deploy

#### Start Services

```bash
# Pull latest code
git pull origin main

# Create .env with production values (never in git!)
cp .env.example .env
nano .env  # Edit with secrets

# Build and start
docker-compose build
docker-compose up -d

# Verify services
docker-compose ps
docker-compose logs -f backend
```

#### Verify Deployment

```bash
# Check services are running
docker ps

# Test backend
curl https://your-domain.com/api/health
# Expected: {"status":"ok"}

# Test frontend
curl https://your-domain.com | head -20
# Should show HTML

# Monitor logs
docker-compose logs -f backend

# Test WebSocket
wscat -c wss://your-domain.com/api/ws
```

### Phase 7: Monitoring & Maintenance

#### Health Checks

```bash
# Backend health
curl https://your-domain.com/api/health

# Database connection
docker exec maars-mongo mongosh -u admin -p "$MONGO_PASSWORD" --eval "db.adminCommand('ping')"

# Disk space
docker exec maars-backend du -sh /app/uploads

# Monitor logs
docker-compose logs --tail 100 backend
```

#### Backups

```bash
# MongoDB backup (daily recommended)
docker exec maars-mongo mongodump \
  --username $MONGO_USER \
  --password $MONGO_PASSWORD \
  --out /backup/$(date +%Y-%m-%d)

# Upload to S3
aws s3 sync /backup/ s3://your-bucket/backups/

# Test restore
mongorestore --drop --dir /backup/latest
```

#### Logs Management

```bash
# Centralize logs to Sentry
# Set SENTRY_DSN in .env

# or use ELK Stack
docker run -d --name elasticsearch ...
docker run -d --name kibana ...

# Configure filebeat to ship logs
```

#### SSL Certificate Renewal

```bash
# Auto-renewal with cron (recommended)
0 0 1 * * acme.sh --renew -d your-domain.com

# Manual renewal
acme.sh --renew -d your-domain.com
docker-compose restart nginx
```

## Kubernetes Deployment

For production with auto-scaling and multi-region support:

### Prerequisites
- `kubectl` configured
- Kubernetes cluster (EKS, GKE, AKS)
- Helm 3+
- Container registry (ECR, GCR, ACR)

### Deploy with Helm

```bash
# Create namespace
kubectl create namespace maars-prod

# Create secrets
kubectl create secret generic maars-secrets \
  --from-literal=mongodb_url=$MONGO_URL \
  --from-literal=jwt_secret=$JWT_SECRET \
  -n maars-prod

# Deploy
helm install maars ./helm/maars-infinity \
  --namespace maars-prod \
  --values production-values.yaml
```

See `helm/maars-infinity/` for chart definitions.

## AWS Deployment (Elastic Beanstalk)

For simpler AWS deployments without Kubernetes:

```bash
# Initialize Elastic Beanstalk
eb init -p python-3.10 maars

# Create environment
eb create maars-prod --instance-type t3.large

# Deploy
eb deploy

# Monitor
eb logs
eb health
```

## Troubleshooting Deployment

### Services won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. MongoDB connection: verify MONGO_URL and credentials
# 2. Port conflicts: check `docker ps` and kill conflicting containers
# 3. Disk space: verify `df -h` shows free space
```

### Database migrations fail
```bash
# Check index creation
docker exec maars-mongo mongosh -u admin -p "$PASS" --eval "db.chats.getIndexes()"

# If missing, restart backend
docker-compose restart backend
```

### High memory usage
```bash
# Check memory
docker stats

# Reduce Node heap size in frontend Dockerfile
# Increase MongoDB memory in docker-compose.yml
```

### SSL certificate errors
```bash
# Verify certificate
openssl x509 -in /etc/letsencrypt/cert.pem -noout -text

# Check Nginx configuration
docker exec maars-nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

## Security Best Practices

### Required

- [ ] Change `JWT_SECRET` to strong random value
- [ ] Use HTTPS only (HTTP redirects to HTTPS)
- [ ] Set `DEBUG=false` in production
- [ ] Configure `CORS_ORIGINS` to specific domain
- [ ] Use managed MongoDB (Atlas) with encryption
- [ ] Enable authentication for all services
- [ ] Use environment variable service (not .env in git)
- [ ] Set up automated backups
- [ ] Configure rate limiting on `/api/auth/*` endpoints
- [ ] Monitor for suspicious activity

### Recommended

- [ ] Enable MongoDB encryption at rest
- [ ] Use VPN/cloud private network
- [ ] Set up Web Application Firewall (WAF)
- [ ] Enable audit logging
- [ ] Use multi-factor authentication for admin accounts
- [ ] Implement API rate limiting
- [ ] Set up DDoS protection
- [ ] Regular security audits
- [ ] Rotate API keys quarterly
- [ ] Monitor third-party API keys (OPENAI, etc.)

### Access Control

- Keep Kubernetes RBAC strict (namespaces, SA, roles)
- Use IAM roles for cloud services (AWS, GCP)
- Implement network policies (only necessary connections)
- Database: create application-specific users (not root)
- Limit SSH access to deployment servers

## Performance Tuning

### MongoDB

```javascript
// Enable query profiling
db.setProfilingLevel(1)

// Add missing indexes
db.chats.createIndex({userId: 1, createdAt: -1})
db.tasks.createIndex({agentId: 1, status: 1})
db.users.createIndex({email: 1}, {unique: true})
```

### Redis Caching (Optional)

For high-traffic deployments, add Redis cache:

```yaml
cache:
  image: redis:7
  restart: always
  ports:
    - "6379:6379"
```

Update backend to use Redis for sessions/caching.

### Scaling

**Horizontal Scaling (Multiple Instances):**
```bash
# With Docker Compose
docker-compose up -d --scale backend=3 --scale frontend=2

# With Kubernetes, adjust replicas
kubectl scale deployment/maars-backend --replicas=3
```

**Vertical Scaling (Larger Instance):**
- Increase RAM allocation to MongoDB
- Increase Node.js heap size in frontend
- Use larger CPU machines

## Rollback Procedure

If deployment fails:

```bash
# Quick rollback
docker-compose down
git checkout previous-stable-tag
docker-compose up -d

# Database rollback (if schemas changed)
mongorestore --drop --dir /backup/last-good-backup
docker-compose restart backend
```

## Post-Deployment

1. **Health Checks**
   - Monitor dashboard: CPU, memory, errors
   - Check API response times
   - Verify all integrations working

2. **Performance Baseline**
   - Measure response times
   - Monitor resource usage
   - Set up alerts

3. **User Communication**
   - Announce deployment
   - Document known issues
   - Provide support contacts

4. **Documentation**
   - Document environment specifics
   - Create runbooks for common issues
   - Update DNS records

## Getting Help

- Check `docker-compose logs` for detailed errors
- Verify all environment variables set correctly
- Test connectivity to MongoDB, APIs, email
- Check GitHub Issues for known problems
- Contact support with descriptive error messages and logs

---

**Last Updated:** 2024-03-26  
**Recommended for:** Production launches with 100+ concurrent users
