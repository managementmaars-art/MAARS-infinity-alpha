# MAARS Infinity - Local Development Setup Guide

Complete step-by-step guide for setting up MAARS Infinity for local development.

## System Requirements

- **Python:** 3.10 or higher
- **Node.js:** 18.0 or higher
- **Yarn:** 1.22.x (comes with Node)
- **MongoDB:** 5.0 or higher
- **Git:** 2.0 or higher
- **Disk Space:** ~5 GB (node_modules + Python packages + development artifacts)
- **RAM:** 4 GB minimum, 8 GB recommended
- **OS:** macOS, Linux, or Windows (with WSL 2 recommended)

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/MAARS-Command.git
cd MAARS-Command
```

## Step 2: Set Up MongoDB

### Using Docker (Recommended)
```bash
docker run -d \
  --name maars-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin \
  mongo:6.0
```

Verify:
```bash
mongosh --eval "db.adminCommand('ping')"
# Expected output: { ok: 1 }
```

### Using Local Installation
See MongoDB official docs: https://docs.mongodb.com/manual/installation/

```bash
# macOS with Homebrew
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt-get install -y mongodb
sudo systemctl start mongodb

# Windows
# Download from https://www.mongodb.com/try/download/community
```

### Using Docker Compose (Alternative)
The project includes `docker-compose.yml` for one-command setup:
```bash
docker-compose up -d mongo
mongosh --eval "db.adminCommand('ping')"
```

## Step 3: Configure Environment Variables

### Backend
```bash
# Copy template and edit
cp .env.example .env

# Edit .env with required values
nano .env  # or use your editor

# Key variables to set:
# MONGO_URL=mongodb://localhost:27017
# DB_NAME=maars_infinity
# JWT_SECRET=your-super-secret-key-change-in-production
```

### Frontend
```bash
cd frontend
cp ../.env.example .env.local
nano .env.local

# Key variable:
# REACT_APP_BACKEND_URL=http://localhost:8000
```

## Step 4: Install Backend Dependencies

```bash
cd backend
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
```

**Expected output:** `FastAPI 0.110.1` (or compatible version)

## Step 5: Start Backend Server

```bash
cd backend
python server.py
```

**Expected output:**
```
[23:45:12] Starting MAARS Command Backend
[23:45:12] Connecting to MongoDB...
[23:45:12] ✓ MongoDB connection successful
[23:45:13] ✓ Seeding default agents and tools
[23:45:14] Uvicorn running on http://0.0.0.0:8000
```

### Verify Backend is Running

In a new terminal:
```bash
# Health check
curl http://localhost:8000/api/health

# Expected response: {"status": "ok"}

# View API docs
open http://localhost:8000/docs
```

## Step 6: Install Frontend Dependencies

In a new terminal:
```bash
cd frontend
yarn install

# Verify installation
yarn --version
# Expected: 1.22.x
```

## Step 7: Start Frontend Development Server

```bash
cd frontend
yarn start
```

**Expected output:**
```
webpack compiled with 3 warnings
Compiled successfully!

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

Open http://localhost:3000 in your browser. You should see the MAARS Infinity dashboard.

## Validation Checklist

After completing all steps, verify:

- [ ] Backend running: `curl http://localhost:8000/api/health` returns `{"status": "ok"}`
- [ ] Frontend accessible: Open `http://localhost:3000` in browser (no error page)
- [ ] MongoDB connected: Check backend logs show `✓ MongoDB connection successful`
- [ ] API docs available: Open `http://localhost:8000/docs` (Swagger UI loads)
- [ ] Frontend can reach backend: Check browser console for no CORS errors
- [ ] No `Cannot find module` errors in terminal

All green? You're ready to develop!

## Development Workflow

### Authentication
Before using the API, create a test account:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@example.com",
    "password": "DemoPass123!",
    "first_name": "Dev",
    "last_name": "User"
  }'
```

Then log in in the frontend UI.

### Running Tests

#### Backend Tests
```bash
cd backend
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass with ✓

#### Frontend Tests
```bash
cd frontend
yarn test --watchAll=false
```

### Code Quality

#### Backend Linting & Formatting
```bash
cd backend
# Check code style
flake8 . --max-line-length=120 --ignore=E501,W503

# Format code
black . --line-length=120
```

#### Frontend Linting
```bash
cd frontend
# Check code style
eslint src/ --max-warnings=0

# Fix issues automatically
eslint src/ --fix
```

### Hot Reload

Both servers support hot reload for development:

- **Backend:** Restart server to pick up changes (no hot reload by default)
- **Frontend:** Changes auto-refresh in browser immediately

To enable backend hot reload with `watchmedo`:
```bash
pip install watchdog
watchmedo auto-restart -d . -p '*.py' -- python server.py
```

## Database Management

### Seed Sample Data
```bash
curl -X POST http://localhost:8000/api/admin/seed-demo-data \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### View Database
Using MongoDB Compass GUI (recommended):
1. Download from https://www.mongodb.com/try/download/compass
2. Connect to `mongodb://localhost:27017`
3. Browse collections and documents

Using command line:
```bash
mongosh
use maars_infinity
db.users.find().pretty()
db.chats.find().limit(1).pretty()
```

### Reset Database
```bash
mongosh maars_infinity
db.dropDatabase()
# Then restart backend - it will re-seed
```

## Environment Variables Guide

**Required** (must set before backend starts):
- `MONGO_URL` — MongoDB connection string
- `DB_NAME` — Database name (e.g., `maars_infinity`)
- `JWT_SECRET` — JWT signing secret (use `openssl rand -hex 32` to generate)

**Recommended** (set at least one LLM provider):
- `OPENAI_API_KEY` — For OpenAI models (GPT-4, GPT-3.5)
- `ANTHROPIC_API_KEY` — For Claude models
- `GOOGLE_API_KEY` — For Gemini models

**Optional** (integrations, can skip initially):
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` — OAuth login
- `SMTP_HOST`, `SMTP_EMAIL`, `SMTP_PASSWORD` — Email sending
- `STRIPE_API_KEY` — Payment processing
- `ELEVENLABS_API_KEY` — Voice synthesis

For a local dev setup with no integrations:
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=maars_infinity
JWT_SECRET=$(openssl rand -hex 32)
OPENAI_API_KEY=optional-but-chatting-requires-one
```

## Troubleshooting

### "Connection refused" when starting backend

**Problem:** Backend can't connect to MongoDB

```
pymongo.errors.ServerSelectionTimeoutError: connection refused
```

**Solutions:**
1. Verify MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
2. Check `MONGO_URL` in `.env` (should be `mongodb://localhost:27017`)
3. Check MongoDB port (default 27017): `lsof -i :27017` (macOS/Linux)
4. Restart MongoDB service:
   - Docker: `docker restart maars-mongo`
   - Homebrew: `brew services restart mongodb-community`
   - System: `sudo systemctl restart mongodb`

### "Port 8000 already in use"

```bash
# macOS/Linux - find process
lsof -i :8000
# Kill process
kill -9 <PID>

# Windows
netstat -ano | grep "LISTENING.*8000"
taskkill /PID <PID> /F
```

Or change port in backend code and `.env`:
```
SERVER_PORT=8001
REACT_APP_BACKEND_URL=http://localhost:8001
```

### "Port 3000 already in use"

```bash
# Kill Node process
lsof -i :3000 | grep node | awk '{print $2}' | xargs kill -9

# Or change port
PORT=3001 yarn start
# Then update browser to http://localhost:3001
```

### Frontend shows "Cannot GET /"

**Problem:** React Router not configured correctly

**Solutions:**
1. Ensure `yarn start` completed without errors
2. Check browser console for JavaScript errors (F12)
3. Hard refresh: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows)
4. Clear cache: Delete `node_modules/.cache` and restart

### "CORS error" - Frontend can't reach backend

```
Access to XMLHttpRequest at 'http://localhost:8000/...' blocked by CORS policy
```

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
3. Verify `REACT_APP_BACKEND_URL` in frontend `.env.local` matches backend URL
4. Restart both servers

Backend `.env`:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Frontend `.env.local`:
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

### "ModuleNotFoundError" in backend

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
1. Verify Python venv is activated: `echo $VIRTUAL_ENV` (macOS/Linux) or `echo %VIRTUAL_ENV%` (Windows)
2. Verify pip installation completed: `pip list | grep fastapi`
3. Reinstall: `pip install -r requirements.txt --force-reinstall`

### "React version mismatch" warning

```
Warning: ReactDOM.render is no longer supported in React 19.
```

This is a library compatibility issue. Safe to ignore for now, but run:
```bash
cd frontend
yarn upgrade
```

### "npm ERR! code ERESOLVE" during yarn install

```
yarn cache clean
rm -rf node_modules yarn.lock
yarn install
```

### Backend crashes on startup with "key error"

Check that all required environment variables are set in `.env`. See [.env.example](.env.example).

Most common missing ones:
- `MONGO_URL`
- `DB_NAME`
- `JWT_SECRET`

### Tests fail with "database connection error"

Reset test database:
```bash
# In MongoDB shell
use maars_infinity_test
db.dropDatabase()

# Then retry tests
cd backend
python -m pytest tests/ -v
```

## Next Steps

- **Read Architecture:** See [memory/MAARS_ARCHITECTURE.md](memory/MAARS_ARCHITECTURE.md)
- **Learn API:** Explore `http://localhost:8000/docs` (interactive Swagger UI)
- **Create First Agent:** See [agents.md](agents.md) for agent builder guide
- **Deploy:** When ready, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Getting Help

- **Documentation:** Check [README.md](README.md), [DEPLOYMENT.md](DEPLOYMENT.md), [agents.md](agents.md)
- **Common Issues:** Search troubleshooting section above
- **API Issues:** Check backend logs in terminal
- **Frontend Issues:** Check browser console (F12)
- **GitHub Issues:** Report bugs with `[Local Setup]` tag

Happy developing! 🚀
