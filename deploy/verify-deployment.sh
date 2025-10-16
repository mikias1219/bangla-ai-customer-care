#!/usr/bin/env bash
set -e

echo "🔍 Verifying deployment on server..."

# Check if services are running
echo "📊 Checking service status..."
sudo systemctl status bangla-frontend --no-pager -l || echo "❌ Frontend service not running"
sudo systemctl status bangla-backend --no-pager -l || echo "❌ Backend service not running"

# Check if processes are listening on ports
echo "🔌 Checking port usage..."
netstat -tlnp | grep :3002 || echo "❌ Nothing listening on port 3002"
netstat -tlnp | grep :8000 || echo "❌ Nothing listening on port 8000"

# Test nginx configuration
echo "🌐 Testing nginx configuration..."
sudo nginx -t && echo "✅ Nginx configuration is valid" || echo "❌ Nginx configuration has errors"

# Test endpoints
echo "🧪 Testing endpoints..."
curl -k https://bdchatpro.com/health 2>/dev/null && echo "✅ Health check passed" || echo "❌ Health check failed"
curl -I https://bdchatpro.com 2>/dev/null | head -1 && echo "✅ HTTPS working" || echo "❌ HTTPS not working"

# Check project directory
echo "📁 Checking project directory..."
ls -la /opt/bangla-ai-customer-care/ 2>/dev/null || echo "❌ Project directory not found"

echo "✅ Verification completed!"
