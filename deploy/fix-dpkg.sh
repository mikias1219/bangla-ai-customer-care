#!/usr/bin/env bash
set -e

echo "🔧 Fixing dpkg configuration issues..."

# Kill any running apt processes
echo "🛑 Killing any running apt processes..."
sudo killall -9 apt apt-get dpkg 2>/dev/null || true

# Remove apt locks
echo "🔓 Removing apt locks..."
sudo rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock

# Configure dpkg
echo "⚙️ Configuring dpkg..."
sudo dpkg --configure -a

# Clean up
echo "🧹 Cleaning up package cache..."
sudo apt clean
sudo apt autoclean

# Fix any broken packages
echo "🔧 Fixing broken packages..."
sudo apt --fix-broken install -y

echo "✅ dpkg configuration fixed! You can now run apt commands."
