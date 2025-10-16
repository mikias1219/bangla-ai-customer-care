#!/usr/bin/env bash
# Fix Nginx Configuration for bdchatpro.com
# Run this on your VPS to troubleshoot and fix the website

set -e

echo "🔍 Bangla AI - Nginx Configuration Diagnostic"
echo "=============================================="
echo ""

# Check if nginx configuration exists
echo "📋 Checking Nginx configuration..."
if [ -f /etc/nginx/sites-available/bangla ]; then
  echo "✅ Bangla configuration file exists"
  echo ""
  echo "📄 Current configuration:"
  cat /etc/nginx/sites-available/bangla
else
  echo "❌ Bangla configuration file NOT found!"
  exit 1
fi

echo ""
echo "🔗 Checking symbolic link..."
if [ -L /etc/nginx/sites-enabled/bangla ]; then
  echo "✅ Symbolic link exists"
  ls -la /etc/nginx/sites-enabled/bangla
else
  echo "❌ Symbolic link NOT found! Creating..."
  sudo ln -sf /etc/nginx/sites-available/bangla /etc/nginx/sites-enabled/bangla
fi

echo ""
echo "🌐 Checking all enabled sites..."
ls -la /etc/nginx/sites-enabled/

echo ""
echo "🔧 Testing Nginx configuration..."
if sudo nginx -t; then
  echo "✅ Nginx configuration is valid"
else
  echo "❌ Nginx configuration has errors!"
  exit 1
fi

echo ""
echo "📂 Checking frontend files..."
if [ -d /var/www/bangla ]; then
  echo "✅ Frontend directory exists"
  echo "Files in /var/www/bangla:"
  ls -lah /var/www/bangla/ | head -20
else
  echo "❌ Frontend directory NOT found!"
  exit 1
fi

echo ""
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ Nginx has been reloaded"

echo ""
echo "🧪 Testing local access..."
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "🎯 Testing bdchatpro.com access..."
curl -H "Host: bdchatpro.com" http://localhost/ 2>&1 | head -50

echo ""
echo "📊 Backend service status:"
sudo systemctl status bangla-backend --no-pager | head -20

echo ""
echo "✅ Diagnostic complete!"
echo ""
echo "If the website still doesn't work, you may need to:"
echo "1. Remove conflicting nginx configurations"
echo "2. Set bangla as the default site"
echo "3. Check firewall rules"

