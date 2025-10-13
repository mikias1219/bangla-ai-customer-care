# Deployment Guide - Bangla AI Platform

This guide covers deploying the Bangla AI Platform to a VPS with OpenAPI docs and social channels (Messenger, Instagram, WhatsApp).

## Prerequisites

- VPS with Ubuntu 22.04+ (4GB RAM, 2 CPU, 40GB disk)
- Domain name pointing to VPS (e.g., api.yourdomain.com)
- SSH access to the VPS
- Docker + Docker Compose installed

## OpenAPI Docs

After deploy, API docs are available at:
- `https://api.yourdomain.com/docs`
- `https://api.yourdomain.com/redoc`

## Quick Deploy

```bash
# Clone & run
cd /opt
sudo git clone <your repo> bangla-ai
cd bangla-ai
cp env.example .env
# Edit .env with secrets and channel tokens

# Start services
./start.sh
```

## Reverse Proxy (Caddy)

Configure Caddy to expose:
- Dashboard: `https://yourdomain.com` -> `localhost:5173`
- API: `https://api.yourdomain.com` -> `localhost:8000`

```
yourdomain.com {
    reverse_proxy localhost:5173
}

api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

## Channel Webhooks

### Meta (Messenger & Instagram)

1. Set environment variables in `.env`:
```
META_VERIFY_TOKEN=your-verify-token
META_APP_SECRET=your-meta-app-secret
MESSENGER_PAGE_ID=...
MESSENGER_PAGE_ACCESS_TOKEN=...
INSTAGRAM_BUSINESS_ID=...
INSTAGRAM_ACCESS_TOKEN=...
```
2. In Meta App Dashboard:
   - Add webhook product and subscribe to messages
   - Callback URL: `https://api.yourdomain.com/channels/meta/webhook`
   - Verify Token: must match `META_VERIFY_TOKEN`
   - Select Page/IG account and subscribe
3. Test:
```bash
curl "https://api.yourdomain.com/channels/meta/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=123"
```

### WhatsApp Business API

1. In `.env`:
```
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_VERIFY_TOKEN=...
```
2. Webhook URL: `https://api.yourdomain.com/channels/whatsapp/webhook`
3. Verify token must match `WHATSAPP_VERIFY_TOKEN`

## VPS Hardening

- Enable UFW (22, 80, 443)
- Disable root SSH login
- Use SSH keys only
- Install fail2ban

## CI/CD (Optional)

This repo includes a GitHub Actions workflow that builds Docker images and deploys to a VPS.

### Configure GitHub

1. Packages registry: images are pushed to GHCR (`ghcr.io`). Ensure the repo has access
   to GitHub Packages and visibility allows package publishing.
2. Set repository secrets/variables:
   - Secrets:
     - `VPS_HOST`: your VPS IP or hostname
     - `VPS_USER`: SSH username on the VPS
     - `VPS_SSH_KEY`: private key (PEM) for SSH
   - Optional variables/secrets:
     - `VITE_API_BASE`: e.g. `https://api.yourdomain.com`

The workflow file: `.github/workflows/deploy.yml`.

It performs:
 - Build and push backend image from `backend/Dockerfile`
 - Build and push dashboard image from `frontend/dashboard/Dockerfile.prod`
 - Copy the `deploy/` folder to the VPS and run `deploy/deploy.sh`

### Configure VPS

On the VPS, the workflow places files under `~/bangla-deploy`. Create `~/bangla-deploy/.env` with:

```
REGISTRY=ghcr.io
OWNER=<your-github-username-or-org>
POSTGRES_PASSWORD=<strong-password>
BANG_SECRET_KEY=<strong-secret>
BANG_CORS_ORIGINS=["https://yourdomain.com","https://api.yourdomain.com"]
VITE_API_BASE=http://backend:8000
# Optional channel credentials... (see env.example)
```

Then the workflow runs:

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec -T backend python scripts/init_db.py
```

## Monitoring (Included)

The production setup includes Prometheus and Grafana for monitoring:

- **Prometheus**: http://yourdomain.com:9090 (metrics collection)
- **Grafana**: http://yourdomain.com:3000 (dashboards, admin/${GRAFANA_ADMIN_PASSWORD})

### Metrics Available

- Backend API requests and performance
- NLU accuracy and fallback rates
- Conversation analytics
- System resource usage

### Setting up Monitoring

1. Set `GRAFANA_ADMIN_PASSWORD` in your `.env` file
2. The services auto-start with the production deployment
3. Access Grafana at `http://yourdomain.com:3000`
4. Default dashboards are pre-configured for Bangla AI metrics

### Adding More Metrics

To add PostgreSQL/Redis exporters:

```yaml
# Add to docker-compose.prod.yml
postgres-exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: postgresql://bangla:${POSTGRES_PASSWORD}@postgres:5432/bangla_ai?sslmode=disable
  ports:
    - "9187:9187"

redis-exporter:
  image: oliver006/redis_exporter
  environment:
    REDIS_ADDR: redis://redis:6379
    REDIS_PASSWORD: ""
  ports:
    - "9121:9121"
```

## Troubleshooting

- `docker compose logs backend` to inspect backend
- Ensure `.env` values are set and service restarted
- Check webhook signature (Meta `X-Hub-Signature-256`) if 403

