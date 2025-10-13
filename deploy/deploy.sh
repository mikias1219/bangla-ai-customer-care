#!/usr/bin/env bash
set -euo pipefail

# Load env if present
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

echo "==> Pulling latest images from ${REGISTRY}/${OWNER}"
docker compose -f docker-compose.prod.yml pull || true

echo "==> Starting services"
docker compose -f docker-compose.prod.yml up -d

echo "==> Waiting for services to be ready..."
sleep 10

echo "==> Running DB migrations/seed if needed"
docker compose -f docker-compose.prod.yml exec -T backend python scripts/init_db.py || true

echo "==> Services status:"
docker compose -f docker-compose.prod.yml ps

echo "==> Done!"
echo ""
echo "Access your application:"
echo "  Dashboard: https://yourdomain.com"
echo "  API Docs: https://yourdomain.com/docs"
echo "  Grafana: https://yourdomain.com:3000 (admin/${GRAFANA_ADMIN_PASSWORD:-admin})"
echo "  Prometheus: https://yourdomain.com:9090"
echo ""
echo "Don't forget to:"
echo "  1. Update your domain DNS records"
echo "  2. Configure SSL certificates"
echo "  3. Set up firewall rules (ufw allow 22,80,443,3000,9090)"


