#!/usr/bin/env bash
set -euo pipefail

# Bangla AI Platform - Production Deployment Script (Direct Deployment - No Docker)
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

echo ""
echo "📦 Deploying application directly to server..."

# Stop existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop bangla-frontend 2>/dev/null || true
sudo systemctl stop bangla-backend 2>/dev/null || true

echo ""
echo "🔧 Setting up backend..."
# Install backend dependencies
python3 -m venv venv --clear
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo ""
echo "🎨 Setting up frontend..."
# Install Node.js dependencies
cd frontend
npm install

# Build the client dashboard
if [ -d "dashboard" ]; then
  cd dashboard
  npm install
  npm run build
  cd ..
fi

# Build the admin dashboard
if [ -d "admin-dashboard" ]; then
  cd admin-dashboard
  npm install
  npm run build
  cd ..
fi

cd ..

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "🗄️  Initializing database..."
source venv/bin/activate
python scripts/init_db.py || echo "⚠️  DB init failed, continuing..."

echo ""
echo "📱 Adding sample products for AI agent demo..."
python scripts/add_sample_products.py || echo "⚠️  Sample products failed, continuing..."

echo ""
echo "▶️ Starting services..."
sudo systemctl start bangla-frontend
sudo systemctl start bangla-backend

echo ""
echo "📊 Services status:"
sudo systemctl status bangla-frontend --no-pager -l || echo "Frontend status check failed"
sudo systemctl status bangla-backend --no-pager -l || echo "Backend status check failed"

echo ""
echo "✅ Deployment complete!"
echo "======================"
echo ""
echo "🌐 Access your application:"
echo "   Dashboard: https://yourdomain.com"
echo "   API Docs:  https://api.yourdomain.com/docs (if using separate domain)"
echo "   Admin API: https://yourdomain.com/api/admin/intents"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  CHANGE THIS IMMEDIATELY IN PRODUCTION!"
echo ""
echo "📋 Next steps:"
echo "   1. Test the application thoroughly"
echo "   2. Configure SSL certificates if not already done"
echo "   3. Set up monitoring and backups"
echo ""
echo "🆘 Troubleshooting:"
echo "   View backend logs: sudo journalctl -u bangla-backend -f"
echo "   View frontend logs: sudo journalctl -u bangla-frontend -f"
echo "   Restart backend: sudo systemctl restart bangla-backend"
echo "   Restart frontend: sudo systemctl restart bangla-frontend"
echo "   Check processes: ps aux | grep -E '(python|node)'"
echo ""
echo "🎉 Your Bangla AI customer service platform is now live!"


