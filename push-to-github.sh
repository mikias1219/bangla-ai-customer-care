#!/bin/bash
# Push Bangla AI project to GitHub
# Run this after creating the GitHub repository

set -e

echo "🚀 Pushing Bangla AI Platform to GitHub"
echo ""

# Check if git remote origin exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "❌ Git remote 'origin' already exists. Remove it first if you want to change the repository."
    echo "   git remote remove origin"
    exit 1
fi

# Get repository URL from user
echo "Enter your GitHub repository URL:"
echo "Example: https://github.com/yourusername/bangla-ai-customer-care.git"
read -r repo_url

if [ -z "$repo_url" ]; then
    echo "❌ No repository URL provided"
    exit 1
fi

# Add remote origin
echo "📡 Adding remote origin: $repo_url"
git remote add origin "$repo_url"

# Push to GitHub
echo "⬆️  Pushing code to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your GitHub repository settings"
echo "2. Add these repository secrets:"
echo "   - VPS_HOST: your VPS IP address"
echo "   - VPS_USER: your SSH username on the VPS"
echo "   - VPS_SSH_KEY: your private SSH key (paste the entire key)"
echo ""
echo "3. Optional: Set repository variable VITE_API_BASE if using a custom API domain"
echo ""
echo "4. Push any changes to trigger deployment to your VPS!"
echo ""
echo "🔗 Repository: $repo_url"
