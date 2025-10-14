# Bangla AI Customer Care Platform

A full-scale Bangla AI customer care platform with NLU, ASR, TTS, multi-channel support (voice + chat), human handoff, and continuous learning.

## Features

### AI & Language Processing
- **Bangla NLU**: Intent classification and entity extraction using BanglaBERT/IndicBERT
- **OpenAI Integration**: GPT-powered responses, sentiment analysis, translation
- **Bangla ASR**: Speech recognition with Whisper optimized for Bangla
- **Bangla TTS**: Natural text-to-speech (Google/Azure/Coqui)
- **Multi-language Support**: Templates and responses in multiple languages

### Communication Channels
- **Multi-channel**: Voice (IVR), WhatsApp, Messenger, Instagram, Web chat, Mobile
- **Unified Inbox**: Single interface for all customer communications
- **Facebook Messenger**: Business messaging integration
- **Instagram Business**: Direct messaging and commerce
- **WhatsApp Business**: Full commerce and messaging support

### E-Commerce & Business Features
- **Product Management**: Catalog management with pricing and inventory
- **Order Management**: Complete order lifecycle with status tracking
- **Customer Management**: Customer profiles, history, and analytics
- **Transaction Processing**: Payment gateway integration support
- **Business Intelligence**: Revenue analytics, customer insights

### Core Platform
- **Dialogue Management**: State tracking, slot filling, context-aware responses
- **Backend Integration**: Connect to CRM/ERP/databases for real-time data
- **Human Handoff**: Seamless escalation to human agents
- **Admin Dashboard**: Manage intents, entities, templates, products, orders, conversations, analytics
- **Continuous Learning**: Collect failed queries, retrain models

## AI Agent Setup & Demo

### 🤖 Instant AI Responses to Customer Queries

The AI agent instantly responds to customer messages by checking the database, just like a human agent would:

**Example Customer Queries & AI Responses:**

```
Customer: "iPhone 15 Pro er dam koto?"
🤖 AI: "**iPhone 15 Pro**
💰 দাম: BDT 1,299.99
📂 ক্যাটাগরি: Smartphones
🏷️ ব্র্যান্ড: Apple
✅ স্টকে আছে (25 পিস)

কিনতে চান? 'অর্ডার করুন' বলুন।"

Customer: "AirPods Pro ache?"
🤖 AI: "❌ **AirPods Pro** বর্তমানে স্টকে নেই।
আপনাকে notify করব যখন স্টকে আসবে?"
```

### Setting Up AI Agent

1. **Add Sample Products:**
```bash
cd backend
python scripts/add_sample_products.py
```

2. **Test AI Responses:**
```bash
python scripts/demo_ai_agent.py
```

3. **Configure API Keys** in `.env`:
```bash
# OpenAI for enhanced responses
BANG_OPENAI_API_KEY=your-openai-key

# Social Media APIs
BANG_WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
BANG_FACEBOOK_PAGE_ACCESS_TOKEN=your-facebook-token
# ... etc
```

### Supported Query Types

The AI agent automatically handles:
- **Price queries**: "iPhone er dam koto?" / "price of laptop?"
- **Availability**: "stock ache?" / "available?"
- **Product info**: "details" / "about" / "features"
- **Recommendations**: "suggest" / "best" / "recommend"
- **Categories**: "laptop category" / "smartphones"
- **Orders**: "buy" / "order" / "purchase"

## Quick Start with Docker

```bash
# Start all services (backend, frontend, postgres, redis)
docker-compose up -d

# Initialize database with seed data
docker-compose exec backend python scripts/init_db.py

# Add sample products for AI agent demo
docker-compose exec backend python scripts/add_sample_products.py

# Access services
# - Dashboard: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

Default admin credentials:
- Username: `admin`
- Password: `admin123` (⚠️ change in production!)

## Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Dashboard)

```bash
cd frontend/dashboard
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Set `VITE_API_BASE` environment variable if backend is not on `http://localhost:8000`.

## API Endpoints

### Core AI
- `POST /nlu/resolve` - Intent and entity resolution
- `POST /dm/decide` - Dialogue decision making
- `POST /resolver/{name}` - Backend data resolution

### Admin
- `GET /admin/intents` - List/manage intents
- `GET /admin/entities` - List/manage entities
- `GET /admin/conversations` - View conversation history
- `GET /admin/templates` - Manage Bangla response templates
- `GET /admin/config` - System configuration
- `GET /admin/metrics` - Analytics and metrics

### Auth
- `POST /auth/token` - Login
- `POST /auth/register` - Register user
- `GET /auth/me` - Current user info

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Voice     │     │    Chat     │     │  Dashboard  │
│   (IVR)     │     │  Channels   │     │   (Admin)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                    │
       └───────────────────┴────────────────────┘
                           │
                  ┌────────▼────────┐
                  │   FastAPI       │
                  │   Backend       │
                  └────────┬────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐   ┌────────▼────────┐   ┌─────▼─────┐
│  NLU/ASR/   │   │   Dialogue      │   │  Resolver │
│  TTS        │   │   Manager       │   │  (CRM/ERP)│
│  Services   │   │                 │   │           │
└─────────────┘   └─────────────────┘   └───────────┘
       │
┌──────▼──────────────────────────┐
│  PostgreSQL + Redis             │
└─────────────────────────────────┘
```

## Configuration

Environment variables (prefix: `BANG_`):

```bash
# Database
BANG_DATABASE_URL=postgresql://bangla:pass@localhost:5432/bangla_ai

# Redis
BANG_REDIS_URL=redis://localhost:6379/0

# JWT
BANG_SECRET_KEY=your-secret-key
BANG_ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Models
BANG_NLU_MODEL_NAME=sagorsarker/bangla-bert-base
BANG_WHISPER_MODEL_SIZE=base
BANG_TTS_PROVIDER=google  # google, azure, coqui

# External APIs (optional)
BANG_GOOGLE_CLOUD_API_KEY=...
BANG_AZURE_SPEECH_KEY=...
```

## Deployment to VPS

1. Install Docker and Docker Compose on your VPS
2. Clone this repository
3. Copy `.env.example` to `.env` and configure
4. Run `docker-compose up -d`
5. Initialize database: `docker-compose exec backend python scripts/init_db.py`
6. Set up reverse proxy (Caddy/Nginx) with TLS
7. Point your domain to the VPS

### Production (Docker images + CI/CD)

- This repo includes a CI workflow to build images and deploy to a VPS.
- Configure repository secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (private key PEM).
- Optionally set `VITE_API_BASE` repo variable for the dashboard.
- The workflow pushes images to GHCR and runs `deploy/deploy.sh` on your VPS using `deploy/docker-compose.prod.yml`.
- On the VPS, create `~/bangla-deploy/.env` with values like:

```
REGISTRY=ghcr.io
OWNER=<your-gh-username-or-org>
POSTGRES_PASSWORD=<strong-password>
BANG_SECRET_KEY=<strong-secret>
BANG_CORS_ORIGINS=["https://yourdomain.com","https://api.yourdomain.com"]
VITE_API_BASE=http://backend:8000
```

## Project Structure

```
bangla/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, settings
│   │   ├── db/            # Database models
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # NLU, ASR, TTS, DM
│   │   └── main.py        # FastAPI app
│   ├── scripts/           # Utility scripts
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── dashboard/         # React admin dashboard
│       ├── src/
│       ├── Dockerfile
│       └── package.json
├── docker-compose.yml
└── README.md
```

## Next Steps

- [ ] Fine-tune NLU model on domain-specific data
- [ ] Implement WhatsApp/Messenger channel adapters
- [ ] Add voice IVR integration (Twilio/Asterisk)
- [ ] Build agent handoff dashboard
- [ ] Set up continuous learning pipeline
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Implement RBAC and audit logs

## License

Proprietary - All rights reserved
# Test deployment commit
# SSH deployment test Tue Oct 14 04:05:18 AM EAT 2025
