#!/usr/bin/env bash
set -euo pipefail

# SSL Certificate Setup Script for bdchatpro.com
# This script sets up Let's Encrypt SSL certificates using Certbot

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

DOMAIN="bdchatpro.com"
EMAIL="${SSL_EMAIL:-admin@bdchatpro.com}"

log_info "🔒 SSL Certificate Setup for $DOMAIN"
echo "======================================"

# Check if running as root (required for certbot)
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root or with sudo for SSL certificate setup."
   log_info "Run: sudo ./deploy/setup-ssl.sh"
   exit 1
fi

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    log_error "Nginx is not installed. Please run VPS setup first: ./deploy/setup-vps.sh"
    exit 1
fi

# Check if Certbot is installed
if ! command -v certbot &> /dev/null; then
    log_info "Installing Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
    log_success "Certbot installed"
fi

# Check DNS resolution
log_info "Checking DNS resolution for $DOMAIN..."
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    log_error "DNS for $DOMAIN is not configured or not propagated yet."
    log_info "Please configure DNS first: ./deploy/setup-dns.sh"
    log_info "You can check DNS propagation at: https://dnschecker.org/"
    exit 1
fi

# Check if certificate already exists
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    log_info "SSL certificate already exists for $DOMAIN"

    # Check certificate expiry
    if openssl x509 -checkend 86400 -noout -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem > /dev/null 2>&1; then
        log_success "SSL certificate is valid (expires in more than 24 hours)"
    else
        log_warning "SSL certificate expires soon. Renewing..."
        certbot renew --cert-name $DOMAIN
        log_success "SSL certificate renewed"
    fi
else
    # Obtain new certificate
    log_info "Obtaining SSL certificate for $DOMAIN..."

    # Stop Nginx temporarily if it's running with the domain
    if systemctl is-active --quiet nginx; then
        systemctl stop nginx
        log_info "Nginx stopped temporarily"
    fi

    # Obtain certificate
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        -d $DOMAIN \
        -d www.$DOMAIN

    # Start Nginx again
    systemctl start nginx
    log_success "SSL certificate obtained for $DOMAIN"
fi

# Configure Nginx with SSL
log_info "Configuring Nginx with SSL certificate..."

# Backup existing config
if [ -f "/etc/nginx/sites-available/bdchatpro" ]; then
    cp /etc/nginx/sites-available/bdchatpro /etc/nginx/sites-available/bdchatpro.backup.$(date +%Y%m%d_%H%M%S)
fi

# Copy our Nginx config
cp /opt/bdchatpro/deploy/nginx.conf /etc/nginx/sites-available/bdchatpro

# Test Nginx configuration
if nginx -t; then
    systemctl reload nginx
    log_success "Nginx configured with SSL"
else
    log_error "Nginx configuration test failed"
    log_info "Restoring previous configuration..."
    mv /etc/nginx/sites-available/bdchatpro.backup.* /etc/nginx/sites-available/bdchatpro 2>/dev/null || true
    systemctl reload nginx
    exit 1
fi

# Setup automatic renewal
log_info "Setting up automatic certificate renewal..."

# Create renewal hook to reload Nginx
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh << 'EOF'
#!/bin/bash
systemctl reload nginx
echo "Nginx reloaded after certificate renewal"
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh

# Test certificate renewal (dry run)
log_info "Testing certificate renewal (dry run)..."
certbot renew --dry-run

# Setup cron job for renewal check (certbot adds this automatically, but let's verify)
if ! crontab -l | grep -q certbot; then
    log_info "Adding certbot renewal to cron..."
    echo "0 12 * * * /usr/bin/certbot renew --quiet" >> /tmp/certbot-cron
    crontab /tmp/certbot-cron
    rm /tmp/certbot-cron
fi

# Test SSL configuration
log_info "Testing SSL configuration..."
if curl -f -s -I https://$DOMAIN > /dev/null; then
    log_success "SSL configuration test passed"
else
    log_warning "SSL configuration test failed - this may be normal if application is not running yet"
fi

# Show certificate information
log_info "SSL Certificate Information:"
echo "Certificate: $(openssl x509 -noout -subject -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d'=' -f2-)"
echo "Issuer: $(openssl x509 -noout -issuer -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d'=' -f2-)"
echo "Valid until: $(openssl x509 -noout -enddate -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d'=' -f2-)"
echo "Serial: $(openssl x509 -noout -serial -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d'=' -f2-)"

echo ""
echo "🔒 SSL Setup Complete!"
echo "======================"
echo ""
echo "📋 Certificate Details:"
echo "Domain: $DOMAIN"
echo "Certificate Path: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "Private Key Path: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "Auto-renewal: Enabled (runs daily at noon)"
echo ""
echo "🧪 Test Commands:"
echo "• Test SSL: openssl s_client -connect $DOMAIN:443 -servername $DOMAIN"
echo "• Check expiry: openssl x509 -noout -dates -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "• Test site: curl -I https://$DOMAIN"
echo ""
echo "🔄 Certificate Renewal:"
echo "• Automatic: Runs daily via cron"
echo "• Manual: certbot renew"
echo "• Dry run: certbot renew --dry-run"
echo ""
echo "📊 SSL Rating:"
echo "Test your SSL at: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
echo "🆘 Troubleshooting:"
echo "• Certificate not found: Run 'certbot certificates' to list certificates"
echo "• Renewal failed: Check logs with 'journalctl -u certbot'"
echo "• Nginx errors: Check '/var/log/nginx/error.log'"
echo "• Permission issues: Ensure certbot runs as root"
echo ""
echo "📞 Let's Encrypt Rate Limits:"
echo "• 50 certificates per domain per week"
echo "• 5 duplicate certificates per week"
echo "• Certificate valid for 90 days"
echo ""

log_success "🎉 SSL certificate setup completed for $DOMAIN!"
