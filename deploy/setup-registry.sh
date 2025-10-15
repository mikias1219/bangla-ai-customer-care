#!/usr/bin/env bash
set -euo pipefail

# Docker Registry Setup Script for bdchatpro.com
# This script helps set up GitHub Container Registry for automated deployments

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
DEFAULT_REGISTRY="ghcr.io"
DEFAULT_OWNER="${GITHUB_REPOSITORY_OWNER:-your-github-username}"

log_info "🐳 Docker Registry Setup for bdchatpro.com"
echo "=============================================="

# Get GitHub username
if [ -n "${GITHUB_REPOSITORY_OWNER:-}" ]; then
    OWNER="$GITHUB_REPOSITORY_OWNER"
else
    echo "Enter your GitHub username:"
    read -r OWNER
fi

REGISTRY="${REGISTRY:-$DEFAULT_REGISTRY}"
BACKEND_IMAGE="$REGISTRY/$OWNER/bangla-backend"
DASHBOARD_IMAGE="$REGISTRY/$OWNER/bangla-dashboard"

log_info "Using registry: $REGISTRY"
log_info "Using owner: $OWNER"
log_info "Backend image: $BACKEND_IMAGE"
log_info "Dashboard image: $DASHBOARD_IMAGE"

# Check if logged in to registry
log_info "Checking Docker registry authentication..."
if ! docker system info > /dev/null 2>&1; then
    log_error "Docker is not running or not accessible"
    exit 1
fi

# Login to GitHub Container Registry
log_info "Logging in to GitHub Container Registry..."
if [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "$GITHUB_TOKEN" | docker login $REGISTRY -u $OWNER --password-stdin
    log_success "Logged in to GitHub Container Registry using token"
elif [ -n "${GITHUB_PAT:-}" ]; then
    echo "$GITHUB_PAT" | docker login $REGISTRY -u $OWNER --password-stdin
    log_success "Logged in to GitHub Container Registry using PAT"
else
    log_warning "No GitHub token found in environment variables"
    log_info "Please run: echo \$GITHUB_TOKEN | docker login $REGISTRY -u $OWNER --password-stdin"
    log_info "Or set GITHUB_TOKEN or GITHUB_PAT environment variables"
fi

# Build and push backend image
log_info "Building backend image..."
cd backend
docker build -t $BACKEND_IMAGE:latest .
log_success "Backend image built"

log_info "Pushing backend image..."
docker push $BACKEND_IMAGE:latest
log_success "Backend image pushed"

# Build and push dashboard image
log_info "Building dashboard image..."
cd ../frontend/dashboard
docker build -t $DASHBOARD_IMAGE:latest .
log_success "Dashboard image built"

log_info "Pushing dashboard image..."
docker push $DASHBOARD_IMAGE:latest
log_success "Dashboard image pushed"

cd ../..

# Update docker-compose.prod.yml with correct image names
log_info "Updating docker-compose.prod.yml with registry images..."
sed -i.bak "s|image: .*bangla-backend.*|image: $BACKEND_IMAGE:latest|" docker-compose.prod.yml
sed -i.bak "s|image: .*bangla-dashboard.*|image: $DASHBOARD_IMAGE:latest|" docker-compose.prod.yml
log_success "Docker Compose updated"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    log_info "Creating .env file from template..."
    cp deploy/env.prod .env
    sed -i.bak "s|REGISTRY=.*|REGISTRY=$REGISTRY|" .env
    sed -i.bak "s|OWNER=.*|OWNER=$OWNER|" .env
    log_warning "⚠️  .env file created from template. Please configure your secrets!"
else
    log_info ".env file already exists"
fi

# Test pulling images
log_info "Testing image pulls..."
docker pull $BACKEND_IMAGE:latest
docker pull $DASHBOARD_IMAGE:latest
log_success "Images pulled successfully"

# Show registry status
log_info "Registry setup completed!"
echo ""
echo "📋 Registry Information:"
echo "Registry: $REGISTRY"
echo "Owner: $OWNER"
echo "Backend Image: $BACKEND_IMAGE"
echo "Dashboard Image: $DASHBOARD_IMAGE"
echo ""
echo "🔧 GitHub Actions Secrets Required:"
echo "In your GitHub repository settings (https://github.com/$OWNER/YOUR_REPO/settings/secrets/actions):"
echo ""
echo "VPS_HOST          - Your VPS IP address or domain"
echo "VPS_USER          - SSH username for VPS (usually 'root' or your username)"
echo "VPS_SSH_KEY       - Private SSH key for VPS access (generate with: ssh-keygen -t ed25519)"
echo "VPS_PORT          - SSH port (default: 22)"
echo ""
echo "🔐 Generate SSH key for GitHub Actions:"
echo "ssh-keygen -t ed25519 -C \"github-actions@bdchatpro.com\" -f ~/.ssh/github_actions"
echo "Then add the public key (~/.ssh/github_actions.pub) to your VPS user's authorized_keys"
echo "And add the private key content to GitHub secret VPS_SSH_KEY"
echo ""
echo "🚀 Deployment Commands:"
echo "• Automatic: Push to main branch (GitHub Actions will deploy)"
echo "• Manual: Run './deploy/deploy.sh' on your VPS"
echo ""
echo "🧪 Test Deployment:"
echo "curl -f https://bdchatpro.com/health"
echo "curl -f https://bdchatpro.com/docs"
echo ""
echo "📊 View Images:"
echo "Open: https://github.com/$OWNER?tab=packages"
echo ""
echo "🆘 Troubleshooting:"
echo "• Check build logs: GitHub Actions tab in your repository"
echo "• Check deployment logs: ssh to VPS and run 'docker compose -f docker-compose.prod.yml logs'"
echo "• Pull manually: docker pull $BACKEND_IMAGE:latest"
echo ""

log_success "🎉 Docker registry setup completed for bdchatpro.com!"
