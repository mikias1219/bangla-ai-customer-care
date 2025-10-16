#!/usr/bin/env bash
# VPS Cleanup Script - Fixes git conflicts and prepares for automated deployment
# Run this once on your VPS to clean up local changes

set -euo pipefail

echo "🧹 Bangla AI - VPS Cleanup Script"
echo "================================="
echo ""

# Navigate to project directory
cd ~/bangla-ai-customer-care || {
    echo "❌ Error: bangla-ai-customer-care directory not found"
    exit 1
}

echo "📂 Current directory: $(pwd)"
echo ""

# Stash any local changes
echo "💾 Stashing local changes..."
git stash --include-untracked || true

# Remove any untracked files that would conflict
echo "🗑️  Removing untracked conflicting files..."
rm -f deploy/nginx.bangla.conf
rm -f deploy/setup_vps.sh
rm -rf deploy/systemd/
rm -f backend/alembic.ini.backup
rm -f backend/.env.backup

# Reset any local modifications
echo "🔄 Resetting local modifications..."
git reset --hard HEAD

# Pull latest changes
echo "⬇️  Pulling latest changes from main..."
git pull origin main

# Verify we're on latest
echo ""
echo "✅ Cleanup complete!"
echo "📌 Current commit: $(git rev-parse --short HEAD)"
echo "🌿 Current branch: $(git branch --show-current)"
echo ""
echo "🚀 Next steps:"
echo "   1. The GitHub Actions workflow will now automatically deploy on push"
echo "   2. Make sure your GitHub secrets are configured:"
echo "      - OPENAI_API"
echo "      - VPS_HOST"
echo "      - VPS_USER"
echo "      - VPS_PATH (e.g., /root/bangla-ai-customer-care)"
echo "      - VPS_SSH_KEY"
echo ""
echo "   3. Optional: Set LETSENCRYPT_EMAIL variable for automatic SSL"
echo ""
echo "✨ Your VPS is now ready for automated deployments!"

