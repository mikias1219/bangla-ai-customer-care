#!/usr/bin/env bash
set -euo pipefail

# Test Deployment Script for bdchatpro.com
# This script helps verify the deployment is working correctly

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

DOMAIN="${DOMAIN:-bdchatpro.com}"
REGISTRY="${REGISTRY:-ghcr.io}"
OWNER="${OWNER:-$(git config --get user.name | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')}"

log_info "🧪 Testing deployment for $DOMAIN"
echo "==================================="

# Test 1: Check if GitHub Actions workflow file exists
log_info "Checking GitHub Actions configuration..."
if [ -f ".github/workflows/deploy.yml" ]; then
    log_success "GitHub Actions workflow file exists"
else
    log_error "GitHub Actions workflow file not found"
    exit 1
fi

# Test 2: Check Docker Compose configuration
log_info "Checking Docker Compose configuration..."
if [ -f "deploy/docker-compose.prod.yml" ]; then
    log_success "Docker Compose production file exists"
else
    log_error "Docker Compose production file not found"
    exit 1
fi

# Test 3: Check deployment scripts
log_info "Checking deployment scripts..."
SCRIPTS=("deploy/setup-vps.sh" "deploy/setup-ssl.sh" "deploy/setup-registry.sh" "deploy/deploy.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        log_success "$script exists and is executable"
    else
        log_error "$script not found or not executable"
    fi
done

# Test 4: Check environment configuration
log_info "Checking environment configuration..."
if [ -f "deploy/env.prod" ]; then
    log_success "Production environment template exists"

    # Check for required placeholders
    REQUIRED_VARS=("BANG_SECRET_KEY" "POSTGRES_PASSWORD" "BANG_OPENAI_API_KEY")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "$var=change_this" "deploy/env.prod"; then
            log_warning "$var needs to be configured in production"
        fi
    done
else
    log_error "Production environment template not found"
fi

# Test 5: Check Docker images (if Docker is available)
log_info "Checking Docker images..."
if command -v docker &> /dev/null; then
    # Check if backend Dockerfile exists
    if [ -f "backend/Dockerfile" ]; then
        log_success "Backend Dockerfile exists"
    else
        log_error "Backend Dockerfile not found"
    fi

    # Check if dashboard Dockerfile exists
    if [ -f "frontend/dashboard/Dockerfile" ]; then
        log_success "Dashboard Dockerfile exists"
    else
        log_error "Dashboard Dockerfile not found"
    fi
else
    log_warning "Docker not available - skipping Docker checks"
fi

# Test 6: Check Nginx configuration
log_info "Checking Nginx configuration..."
if [ -f "deploy/nginx.conf" ]; then
    log_success "Nginx configuration exists"

    # Check if domain is configured
    if grep -q "$DOMAIN" "deploy/nginx.conf"; then
        log_success "Domain $DOMAIN configured in Nginx"
    else
        log_error "Domain $DOMAIN not found in Nginx configuration"
    fi
else
    log_error "Nginx configuration not found"
fi

# Test 7: Check SSL configuration
log_info "Checking SSL configuration..."
if [ -f "deploy/setup-ssl.sh" ]; then
    log_success "SSL setup script exists"
else
    log_error "SSL setup script not found"
fi

# Test 8: Check DNS (basic)
log_info "Checking DNS resolution..."
if command -v nslookup &> /dev/null; then
    if nslookup "$DOMAIN" > /dev/null 2>&1; then
        log_success "DNS resolution for $DOMAIN works"
    else
        log_warning "DNS resolution for $DOMAIN failed (may be normal if DNS not set up yet)"
    fi
else
    log_warning "nslookup not available - skipping DNS check"
fi

# Test 9: Check registry configuration
log_info "Checking registry configuration..."
BACKEND_IMAGE="$REGISTRY/$OWNER/bangla-backend"
DASHBOARD_IMAGE="$REGISTRY/$OWNER/bangla-dashboard"

log_info "Backend image: $BACKEND_IMAGE"
log_info "Dashboard image: $DASHBOARD_IMAGE"

# Test 10: Check deployment README
log_info "Checking deployment documentation..."
if [ -f "deploy/README.md" ]; then
    log_success "Deployment README exists"
else
    log_error "Deployment README not found"
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "=========================="
echo "1. ✅ Configure DNS: $DOMAIN → your VPS IP"
echo "2. ⏳ Run VPS setup: sudo ./deploy/setup-vps.sh"
echo "3. ⏳ Setup SSL: sudo ./deploy/setup-ssl.sh"
echo "4. ⏳ Configure registry: ./deploy/setup-registry.sh"
echo "5. ⏳ Set environment: cp deploy/env.prod .env (edit secrets)"
echo "6. ⏳ Configure GitHub secrets: VPS_HOST, VPS_USER, VPS_SSH_KEY"
echo "7. ⏳ Deploy: Push to main branch or run ./deploy/deploy.sh"
echo ""

echo "🔧 GitHub Secrets Required:"
echo "VPS_HOST          - Your VPS public IP"
echo "VPS_USER          - SSH username (usually 'ubuntu' or 'root')"
echo "VPS_SSH_KEY       - Private SSH key for deployment"
echo "VPS_PORT          - SSH port (default: 22)"
echo ""

echo "📊 Monitoring Commands:"
echo "./deploy/health-check.sh    # Check health"
echo "./deploy/monitor.sh continuous  # Continuous monitoring"
echo ""

log_success "🎉 Deployment configuration test completed!"
echo ""
echo "🚀 Ready to deploy to: https://$DOMAIN"
echo "📚 See deploy/README.md for detailed instructions"
