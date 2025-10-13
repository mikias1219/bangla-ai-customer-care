# Bangla AI Platform - Quick Reference

## 🚀 Getting Started

### First Time Setup
```bash
# 1. Start services
./start.sh

# 2. Access dashboard
open http://localhost:5173

# 3. Login
Username: admin
Password: admin123
```

### Manual Start
```bash
# Start all services
docker-compose up -d

# Initialize database (first time only)
docker-compose exec backend python scripts/init_db.py

# View logs
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

---

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Test NLU
```bash
curl -X POST http://localhost:8000/nlu/resolve \
  -H "Content-Type: application/json" \
  -d '{"text": "Amar order 123 kothay?"}'
```

### Test Dialogue Manager
```bash
curl -X POST http://localhost:8000/dm/decide \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "order_status",
    "entities": {"order_id": "123"},
    "context": {"channel": "web"}
  }'
```

### Get Intents
```bash
curl http://localhost:8000/admin/intents
```

### Get Templates
```bash
curl http://localhost:8000/admin/templates
```

---

## 🔐 Authentication

### Login
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Register New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "role": "viewer"
  }'
```

### Get Current User
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗄️ Database Operations

### Connect to Database
```bash
docker-compose exec postgres psql -U bangla -d bangla_ai
```

### Common SQL Queries
```sql
-- List all intents
SELECT * FROM intents;

-- List all conversations
SELECT * FROM conversations ORDER BY started_at DESC LIMIT 10;

-- Count conversations by channel
SELECT channel, COUNT(*) FROM conversations GROUP BY channel;

-- List all users
SELECT username, email, role, is_active FROM users;
```

### Backup Database
```bash
docker-compose exec postgres pg_dump -U bangla bangla_ai > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker-compose exec -T postgres psql -U bangla -d bangla_ai
```

---

## 📊 Monitoring

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Resource Usage
```bash
docker stats
```

### Disk Usage
```bash
docker system df
```

---

## 🔧 Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Rebuild backend
docker-compose build backend
docker-compose up -d backend
```

### Database Connection Error
```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Check if port 5173 is available
lsof -i :5173
```

### Clear Everything and Start Fresh
```bash
# Stop and remove all containers, volumes, and networks
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
./start.sh
```

---

## 🧪 Testing

### Test NLU Service
```python
# In Python shell
from app.services.nlu_service import nlu_service

result = nlu_service.resolve("Amar order 123 kothay?")
print(result)
```

### Test Dialogue Manager
```python
from app.services.dialogue_manager import dialogue_manager

result = dialogue_manager.decide(
    intent="order_status",
    entities={"order_id": "123"},
    context={"channel": "web"}
)
print(result)
```

### Test Template Engine
```python
from app.services.template_engine import template_engine

text = template_engine.render(
    "order_status",
    {"order_id": "123", "status": "In Transit", "delivery_date": "2025-10-15"}
)
print(text)
```

---

## 📝 Common Tasks

### Add New Intent
```bash
curl -X POST http://localhost:8000/admin/intents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_intent",
    "description": "Description here",
    "status": "active"
  }'
```

### Add New Entity
```bash
curl -X POST http://localhost:8000/admin/entities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "entity_name",
    "entity_type": "regex",
    "pattern": "\\d+",
    "description": "Description here"
  }'
```

### Add New Template
```bash
curl -X POST http://localhost:8000/admin/templates \
  -H "Content-Type: application/json" \
  -d '{
    "key": "template_key",
    "lang": "bn-BD",
    "body": "Template body with {variable}",
    "variables": ["variable"]
  }'
```

---

## 🔄 Updates & Maintenance

### Update Code
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Update Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend/dashboard
npm install
```

### Clean Up Docker
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Clean everything
docker system prune -a --volumes
```

---

## 🌐 Channels

### Test WhatsApp Webhook
```bash
# Verify webhook
curl "http://localhost:8000/channels/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=12345"

# Send test message
curl -X POST http://localhost:8000/channels/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "id": "msg_id",
            "timestamp": "1234567890",
            "text": {"body": "Amar order 123 kothay?"},
            "type": "text"
          }]
        }
      }]
    }]
  }'
```

### Test WebChat
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/channels/webchat/ws');

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};

// Send message
ws.send(JSON.stringify({
  type: 'message',
  text: 'Amar order 123 kothay?',
  timestamp: Date.now()
}));
```

---

## 📚 Documentation

- **README**: General overview and quick start
- **DEPLOYMENT**: VPS deployment guide
- **FEATURES**: Detailed feature documentation
- **PROJECT_STATUS**: Current status and roadmap
- **QUICKREF**: This file - common commands
- **API Docs**: http://localhost:8000/docs

---

## 🆘 Support

### Check Service Health
```bash
# Backend
curl http://localhost:8000/health

# Database
docker-compose exec postgres pg_isready -U bangla

# Redis
docker-compose exec redis redis-cli ping
```

### Get Service Info
```bash
# Backend version
curl http://localhost:8000/ | jq

# Database version
docker-compose exec postgres psql -U bangla -c "SELECT version();"

# Redis info
docker-compose exec redis redis-cli info server
```

### Export Logs
```bash
# Export all logs
docker-compose logs > logs.txt

# Export specific service logs
docker-compose logs backend > backend-logs.txt
```

---

## 🔑 Environment Variables

### View Current Config
```bash
# Backend
docker-compose exec backend python -c "from app.core.config import settings; print(settings.dict())"

# Database URL
echo $BANG_DATABASE_URL
```

### Update Config
```bash
# Edit .env file
nano .env

# Restart services to apply
docker-compose restart
```

---

## 💡 Tips & Tricks

### Run Commands in Container
```bash
# Backend Python shell
docker-compose exec backend python

# Backend bash shell
docker-compose exec backend bash

# Database shell
docker-compose exec postgres bash
```

### Copy Files
```bash
# From container to host
docker cp bangla_backend:/app/file.txt ./

# From host to container
docker cp ./file.txt bangla_backend:/app/
```

### Inspect Container
```bash
# Get container IP
docker inspect bangla_backend | grep IPAddress

# Get environment variables
docker inspect bangla_backend | grep -A 20 Env
```

---

## 🎯 Performance Tips

1. **Use Redis Caching**: Templates and NLU results are cached
2. **Connection Pooling**: SQLAlchemy uses connection pooling
3. **Async Operations**: FastAPI handles requests asynchronously
4. **Model Loading**: Models are lazy-loaded on first use
5. **Database Indexing**: Key fields are indexed for fast queries

---

## 🔐 Security Checklist

- [ ] Change default admin password
- [ ] Update `BANG_SECRET_KEY` in `.env`
- [ ] Update database password
- [ ] Configure CORS origins for your domain
- [ ] Enable HTTPS (use Caddy or Nginx)
- [ ] Set up firewall rules
- [ ] Enable fail2ban
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

---

## 📞 Quick Links

- Dashboard: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

**Last Updated**: October 2025

