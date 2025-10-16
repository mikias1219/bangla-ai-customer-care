#!/usr/bin/env bash
echo "🔧 Quick Node.js/npm fix..."
sudo apt remove --purge -y npm 2>/dev/null || true
sudo apt autoremove -y
sudo apt autoclean
if command -v npm &> /dev/null; then
  echo "✅ npm working: $(npm --version)"
else
  sudo apt install -y nodejs
fi
node --version && npm --version && echo "🎉 Fixed!" || echo "❌ Still broken"
