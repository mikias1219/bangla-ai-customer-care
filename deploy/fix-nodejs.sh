#!/usr/bin/env bash
set -e

echo "🔧 Fixing Node.js and npm installation issues..."

# Check current status
echo "🔍 Checking current Node.js installation..."
if command -v node &> /dev/null; then
  echo "✅ Node.js found: $(node --version)"
else
  echo "❌ Node.js not found"
fi

if command -v npm &> /dev/null; then
  echo "✅ npm found: $(npm --version)"
else
  echo "❌ npm not found"
fi

# Fix broken packages first
echo "🔧 Fixing broken packages..."
sudo apt --fix-broken install -y

# Try to install npm properly
echo "📦 Installing npm..."
if ! sudo apt install -y npm; then
  echo "⚠️  Standard npm installation failed, trying alternative approach..."

  # Remove conflicting packages
  echo "🗑️ Removing conflicting packages..."
  sudo apt remove --purge -y npm node-* 2>/dev/null || true
  sudo apt autoremove -y
  sudo apt autoclean

  # Reinstall Node.js and npm
  echo "🔄 Reinstalling Node.js and npm..."
  sudo apt install -y nodejs npm
fi

# Update npm to latest version
echo "⬆️ Updating npm to latest version..."
sudo npm install -g npm@latest

# Verify installation
echo "🔍 Verifying installations..."
node --version && echo "✅ Node.js: $(node --version)"
npm --version && echo "✅ npm: $(npm --version)"

# Clear npm cache
echo "🧹 Clearing npm cache..."
npm cache clean --force

echo "✅ Node.js and npm installation completed successfully!"
