# MAARS Command — New Device Migration Guide

## 1. Clone the Repository

```bash
git clone https://github.com/managementmaars-art/MAARS-infinity-alpha.git MAARS-Command
cd MAARS-Command
```

## 2. Set Git Identity

```bash
git config user.email "management.maars@marsgc.net"
git config user.name "managementmaars-art"
```

## 3. Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| MongoDB | 6+ (local or Atlas URI) |

## 4. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` with the following (fill in real values):

```env
# === REQUIRED: Real credentials — transfer these manually ===
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>

# === MongoDB ===
MONGODB_URI=mongodb://localhost:27017
DB_NAME=maars_db

# === JWT ===
JWT_SECRET=<generate a strong random secret>
JWT_ALGORITHM=HS256

# === LLM API Keys (fill in your actual keys) ===
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key

# === Stripe (fill in your actual keys) ===
STRIPE_API_KEY=your-stripe-api-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# === App ===
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

> **Note:** Copy the real values from your old device's `backend/.env` before wiping it.

Start the backend:

```bash
cd backend
uvicorn server:app --reload --port 8000
```

## 5. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

Start the frontend:

```bash
npm start
```

## 6. Skills Seeding (optional, if DB is fresh)

The skill catalog (~58k cleaned SKILL.md files) lives at `.claude/skills/` and is
loaded by the backend at agent creation time. To (re)ingest into MongoDB:

```bash
python backend/scripts/ingest_skills.py
```

Historical batch-creation scripts from earlier migrations (create_skills_batch*.py,
harvest_all_skills.py, fetch_skillsmp*.py, etc.) are archived in `scripts/legacy/`
for reference only — they are no longer part of the normal setup flow.

## 7. Docker (alternative to manual setup)

```bash
# Copy backend/.env first (step 4 above), then:
docker-compose up --build
```

Frontend: http://localhost:3000  
Backend: http://localhost:8000  
API docs: http://localhost:8000/docs

## 8. Admin Account

Use `register_user.py` to seed the admin user, or create via the app signup flow with:

- Email: `management.maars@marsgc.net`

## 9. GitHub Remote

```
https://github.com/managementmaars-art/MAARS-infinity-alpha.git
```

Branch: `main`

---

**Critical secrets that are NOT in git and must be transferred manually:**

- `GOOGLE_CLIENT_SECRET` — see step 4 above
- All LLM API keys (OpenAI, Anthropic, Groq, etc.)
- Stripe keys
- JWT secret
- MongoDB URI (if using Atlas)
