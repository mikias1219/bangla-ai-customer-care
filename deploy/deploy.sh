#!/usr/bin/env bash
set -euo pipefail

# Bangla AI Platform - Production Deployment Script
# Run this on your VPS after setting up the environment

echo "🚀 Bangla AI Platform - Production Deployment"
echo "=============================================="

# Load environment variables
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
  echo "✓ Environment variables loaded"
else
  echo "❌ .env file not found. Please create it first."
  echo "   Copy deploy/.env.prod to .env and configure your settings."
  exit 1
fi

# Check required variables
if [ -z "${REGISTRY:-}" ] || [ -z "${OWNER:-}" ]; then
  echo "❌ REGISTRY and OWNER must be set in .env"
  exit 1
fi

echo ""
echo "📦 Pulling latest images from ${REGISTRY}/${OWNER}"
docker compose -f deploy/docker-compose.prod.yml pull || echo "⚠️  Some images not found, using local builds"

echo ""
echo "🐳 Starting services..."
docker compose -f deploy/docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

echo ""
echo "🗄️  Initializing database..."
docker compose -f deploy/docker-compose.prod.yml exec -T backend python scripts/init_db.py || echo "⚠️  DB init failed, continuing..."

echo ""
echo "📱 Adding sample products for AI agent demo..."
docker compose -f deploy/docker-compose.prod.yml exec -T backend python scripts/add_sample_products.py || echo "⚠️  Sample products failed, continuing..."

echo ""
echo "📊 Services status:"
docker compose -f deploy/docker-compose.prod.yml ps

echo ""
echo "✅ Deployment complete!"
echo "======================"
echo ""
echo "🌐 Access your application:"
echo "   Dashboard: https://yourdomain.com"
echo "   API Docs:  https://api.yourdomain.com/docs (if using separate domain)"
echo "   Admin API: https://yourdomain.com/api/admin/intents"
echo ""
echo "📈 Monitoring (optional):"
echo "   Grafana:   https://yourdomain.com:3000"
echo "   Prometheus: https://yourdomain.com:9090"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  CHANGE THIS IMMEDIATELY IN PRODUCTION!"
echo ""
echo "📋 Next steps:"
echo "   1. Update DNS records to point to your VPS"
echo "   2. Configure Caddy reverse proxy (see Caddyfile)"
echo "   3. Set up SSL certificates (automatic with Caddy)"
echo "   4. Configure social media webhooks if needed"
echo "   5. Test the application thoroughly"
echo ""
echo "🆘 Troubleshooting:"
echo "   View logs: docker compose -f deploy/docker-compose.prod.yml logs -f"
echo "   Restart:   docker compose -f deploy/docker-compose.prod.yml restart"
echo "   Stop:      docker compose -f deploy/docker-compose.prod.yml down"
echo ""
echo "🎉 Your Bangla AI customer service platform is now live!"


