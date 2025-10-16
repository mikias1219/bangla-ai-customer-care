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

# The issue: Node.js from nodesource comes with npm bundled, but Ubuntu's npm package conflicts
# Solution: Remove Ubuntu's npm package and use the one that comes with Node.js

echo "🔧 Removing conflicting Ubuntu npm package..."
sudo apt remove --purge -y npm 2>/dev/null || true

echo "🧹 Cleaning up package conflicts..."
sudo apt autoremove -y
sudo apt autoclean

# Check if npm is available through Node.js
echo "🔍 Checking if npm is available through Node.js..."
if command -v npm &> /dev/null; then
  echo "✅ npm is working through Node.js: $(npm --version)"
else
  echo "⚠️  npm still not available, trying to reinstall Node.js..."
  # Reinstall Node.js (which should bring npm with it)
  sudo apt install -y nodejs
fi

# Make sure npm is working
if command -v npm &> /dev/null; then
  # Update npm to latest version using itself
  echo "⬆️ Updating npm to latest version..."
  sudo npm install -g npm@latest 2>/dev/null || echo "⚠️  npm update failed, but npm should still work"

  # Clear npm cache
  echo "🧹 Clearing npm cache..."
  npm cache clean --force 2>/dev/null || true
else
  echo "❌ npm is still not working. Manual intervention may be needed."
  exit 1
fi

# Verify installation
echo "🔍 Verifying installations..."
node --version && echo "✅ Node.js: $(node --version)"
npm --version && echo "✅ npm: $(npm --version)"

echo "✅ Node.js and npm installation completed successfully!"
