# Production Deployment Guide for bdchatpro.com

This guide provides a complete automated deployment setup for the Bangla AI Platform using bdchatpro.com domain.

## 🚀 Quick Start

### Prerequisites
- VPS server (Ubuntu 20.04+ recommended)
- Domain: bdchatpro.com
- GitHub repository with this codebase

### One-Command Setup (VPS)
```bash
# On your VPS as root/sudo user
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy/setup-vps.sh | bash
```

## 📋 Deployment Steps

### 1. DNS Configuration
Configure DNS records for bdchatpro.com:

```bash
# Run this script to get DNS commands
./deploy/setup-dns.sh
```

**Required DNS Records:**
- `bdchatpro.com` → A record to your VPS IP
- `www.bdchatpro.com` → A record to your VPS IP
- `api.bdchatpro.com` → A record to your VPS IP (optional)

### 2. VPS Setup
Run the automated VPS setup script:

```bash
# Download and run VPS setup
sudo ./deploy/setup-vps.sh
```

This script will:
- Update system packages
- Install Docker, Nginx, Certbot
- Configure firewall and security
- Set up automatic updates
- Create application directory structure

### 3. SSL Certificate Setup
Set up Let's Encrypt SSL certificates:

```bash
# Run SSL setup (requires DNS to be configured first)
sudo ./deploy/setup-ssl.sh
```

### 4. Docker Registry Setup
Configure GitHub Container Registry for automated deployments:

```bash
# Setup registry authentication and build images
./deploy/setup-registry.sh
```

### 5. Environment Configuration
Configure production environment variables:

```bash
# Copy and edit environment template
cp deploy/env.prod .env

# Edit with your secrets
nano .env
```

**Required Environment Variables:**
- `BANG_SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `POSTGRES_PASSWORD` - Strong database password
- `BANG_OPENAI_API_KEY` - Your OpenAI API key
- Registry credentials for Docker

### 6. GitHub Actions Setup
Configure automated CI/CD:

1. **GitHub Secrets** (Repository Settings → Secrets and variables → Actions):
   ```
   VPS_HOST          - Your VPS IP address
   VPS_USER          - SSH username (usually 'ubuntu' or 'root')
   VPS_SSH_KEY       - Private SSH key content
   VPS_PORT          - SSH port (default: 22)
   ```

2. **Generate SSH Key for GitHub Actions:**
   ```bash
   # On your local machine
   ssh-keygen -t ed25519 -C "github-actions@bdchatpro.com" -f ~/.ssh/github_actions

   # Copy public key to VPS
   ssh-copy-id -i ~/.ssh/github_actions.pub user@your-vps-ip

   # Add private key to GitHub secret
   cat ~/.ssh/github_actions  # Copy this content to VPS_SSH_KEY
   ```

### 7. Deploy Application
Deploy the application:

```bash
# Manual deployment
./deploy/deploy.sh

# Or automatic via GitHub Actions (push to main branch)
```

## 🏗️ Architecture

```
Internet → Nginx (SSL/TLS) → Backend API (FastAPI)
                    ↓
               Frontend (React SPA)
                    ↓
         PostgreSQL + Redis (Docker)
```

## 🔧 Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `nginx.conf` | Nginx reverse proxy config | `/etc/nginx/sites-available/bdchatpro` |
| `docker-compose.prod.yml` | Production Docker services | `/opt/bdchatpro/` |
| `env.prod` | Environment variables template | `/opt/bdchatpro/.env` |
| `deploy.yml` | GitHub Actions CI/CD | `.github/workflows/` |

## 📊 Monitoring & Health Checks

### Health Check
Run comprehensive health checks:

```bash
# One-time health check
./deploy/health-check.sh

# Continuous monitoring
./deploy/monitor.sh continuous
```

### Monitoring Features
- Application health endpoints
- SSL certificate expiry
- System resources (CPU, memory, disk)
- Docker service status
- Database connectivity
- Automatic alerts via email

## 🔒 Security Features

- **SSL/TLS**: Automatic Let's Encrypt certificates
- **Firewall**: UFW with minimal open ports
- **Fail2Ban**: SSH brute force protection
- **Automatic Updates**: Security patches
- **Rate Limiting**: Built into Nginx config
- **Security Headers**: XSS, CSRF, HSTS protection

## 🚀 Automated Deployment Flow

```mermaid
graph LR
    A[Push to GitHub] --> B[GitHub Actions]
    B --> C[Build Docker Images]
    C --> D[Push to GHCR]
    D --> E[SSH to VPS]
    E --> F[Pull Images]
    F --> G[Deploy Services]
    G --> H[Health Check]
    H --> I[Success/Failure]
```

## 📋 Maintenance Tasks

### Daily
- Automatic SSL renewal (certbot cron)
- Security updates (unattended-upgrades)
- Log rotation

### Weekly
```bash
# Check system health
./deploy/health-check.sh

# Backup database
./backup.sh

# Monitor logs
docker compose -f docker-compose.prod.yml logs --since 7d | grep -i error
```

### Monthly
```bash
# Update SSL certificates manually if needed
sudo certbot renew

# Check disk usage
df -h

# Review monitoring logs
tail -f /opt/bdchatpro/logs/monitor.log
```

## 🆘 Troubleshooting

### Common Issues

**DNS not resolving:**
```bash
# Check DNS propagation
dig bdchatpro.com

# Use online DNS checker
# https://dnschecker.org/
```

**SSL certificate issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --cert-name bdchatpro.com
```

**Application not starting:**
```bash
# Check Docker logs
docker compose -f docker-compose.prod.yml logs -f

# Check service status
docker compose -f docker-compose.prod.yml ps

# Restart services
docker compose -f docker-compose.prod.yml restart
```

**GitHub Actions failing:**
```bash
# Check SSH connection
ssh -T user@vps-ip

# Verify secrets in GitHub
# Repository Settings → Secrets and variables → Actions
```

### Logs Locations
- **Application**: `docker compose -f docker-compose.prod.yml logs -f`
- **Nginx**: `/var/log/nginx/bdchatpro.access.log`
- **System**: `sudo journalctl -u bdchatpro`
- **Monitoring**: `/opt/bdchatpro/logs/monitor.log`

## 📞 Support

For issues:
1. Check health status: `./deploy/health-check.sh`
2. Review logs: `docker compose -f docker-compose.prod.yml logs -f`
3. Check monitoring: `tail -f /opt/bdchatpro/logs/monitor.log`
4. Verify configuration: `nginx -t && docker compose -f docker-compose.prod.yml config`

## 🎯 Performance Optimization

### Nginx Tuning
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;
```

### Database Optimization
```sql
-- Run in PostgreSQL
CREATE INDEX CONCURRENTLY idx_conversations_created ON conversations(created_at);
ANALYZE;
```

### Redis Optimization
```redis
# In redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 🔄 Backup Strategy

### Automated Backups
```bash
# Database backup (daily via cron)
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U bangla bangla_ai > backup_$(date +%Y%m%d).sql

# File backup
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/bdchatpro/.env /opt/bdchatpro/logs/
```

### Restore Procedure
```bash
# Restore database
docker compose -f docker-compose.prod.yml exec -T postgres psql -U bangla bangla_ai < backup.sql

# Restore files
tar -xzf backup.tar.gz -C /
```

---

## ✅ Checklist

- [ ] DNS configured and propagated
- [ ] VPS setup completed (`./deploy/setup-vps.sh`)
- [ ] SSL certificates obtained (`./deploy/setup-ssl.sh`)
- [ ] Docker registry configured (`./deploy/setup-registry.sh`)
- [ ] Environment variables configured (`.env`)
- [ ] GitHub Actions secrets configured
- [ ] SSH key generated and added to VPS
- [ ] Application deployed successfully
- [ ] Health checks passing
- [ ] Monitoring enabled
- [ ] Backup strategy implemented

🎉 **Your bdchatpro.com deployment is now complete and production-ready!**
