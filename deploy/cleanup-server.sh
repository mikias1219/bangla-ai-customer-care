#!/usr/bin/env bash
set -e

echo "🧹 Cleaning up existing bangla-ai-customer-care deployment..."

# Stop and remove existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop bangla-frontend 2>/dev/null || true
sudo systemctl stop bangla-backend 2>/dev/null || true

# Remove systemd service files
echo "🗑️ Removing systemd services..."
sudo rm -f /etc/systemd/system/bangla-frontend.service
sudo rm -f /etc/systemd/system/bangla-backend.service
sudo systemctl daemon-reload

# Remove nginx configuration
echo "🌐 Removing nginx configuration..."
sudo rm -f /etc/nginx/sites-available/bangla
sudo rm -f /etc/nginx/sites-enabled/bangla
sudo systemctl reload nginx 2>/dev/null || true

# Remove the entire project folder
echo "🗂️ Removing existing project folder..."
sudo rm -rf /opt/bangla-ai-customer-care

# Create fresh project directory
echo "📁 Creating fresh project directory..."
sudo mkdir -p /opt/bangla-ai-customer-care
sudo chown $USER:$USER /opt/bangla-ai-customer-care

# Kill any running processes on the ports we need
echo "🔪 Killing any processes using ports 3002 and 8000..."
sudo fuser -k 3002/tcp 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true

# Clean up any apt locks
echo "🔓 Cleaning up apt locks..."
sudo rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock
sudo killall -9 apt apt-get dpkg 2>/dev/null || true

echo "✅ Server cleanup completed!"
echo ""
echo "🎯 Ready for fresh deployment. Run the GitHub Actions workflow now."
