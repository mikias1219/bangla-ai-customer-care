#!/usr/bin/env bash
set -euo pipefail

# VPS Setup Script for bdchatpro.com
# This script sets up a production-ready VPS with all necessary components

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root. Please run as a regular user with sudo access."
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    log_error "sudo is required but not installed. Please install sudo first."
    exit 1
fi

log_info "🚀 Starting VPS setup for bdchatpro.com"
echo "=============================================="

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
log_success "System updated"

# Install essential packages
log_info "Installing essential packages..."
sudo apt install -y curl wget git htop ufw fail2ban unattended-upgrades apt-transport-https ca-certificates gnupg lsb-release jq


# Install Nginx
log_info "Installing Nginx..."
sudo apt install -y nginx
sudo systemctl enable nginx
log_success "Nginx installed"

# Install Certbot for SSL
log_info "Installing Certbot for SSL certificates..."
sudo apt install -y certbot python3-certbot-nginx
log_success "Certbot installed"

# Configure firewall
log_info "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force reload
log_success "Firewall configured"

# Create application directory
log_info "Creating application directory..."
sudo mkdir -p /opt/bdchatpro
sudo chown -R $USER:$USER /opt/bdchatpro
log_success "Application directory created"

# Setup swap space if needed
if [ ! -f /swapfile ]; then
    log_info "Setting up swap space..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    log_success "Swap space configured"
fi

# Configure automatic updates
log_info "Configuring automatic security updates..."
sudo dpkg-reconfigure --priority=low unattended-upgrades
log_success "Automatic updates configured"

# Setup log rotation
log_info "Setting up log rotation..."
sudo tee /etc/logrotate.d/bdchatpro > /dev/null <<EOF
/opt/bdchatpro/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload bdchatpro > /dev/null 2>&1 || true
    endscript
}
EOF
log_success "Log rotation configured"

# Create deployment user (optional)
read -p "Create a deployment user? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Creating deployment user..."
    sudo useradd -m -s /bin/bash deploy
    sudo mkdir -p /home/deploy/.ssh
    sudo chown deploy:deploy /home/deploy/.ssh
    sudo chmod 700 /home/deploy/.ssh
    log_info "Deployment user 'deploy' created. Add SSH keys to /home/deploy/.ssh/authorized_keys"
fi

# Setup Nginx configuration
log_info "Setting up Nginx configuration..."
sudo cp /opt/bdchatpro/deploy/nginx.conf /etc/nginx/sites-available/bdchatpro
sudo ln -sf /etc/nginx/sites-available/bdchatpro /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
log_success "Nginx configured"

# Setup SSL certificates
log_info "Setting up SSL certificates..."
if [ -f "/etc/letsencrypt/live/bdchatpro.com/fullchain.pem" ]; then
    log_info "SSL certificate already exists"
else
    log_info "Obtaining SSL certificate for bdchatpro.com..."
    sudo certbot --nginx -d bdchatpro.com -d www.bdchatpro.com --non-interactive --agree-tos --email admin@bdchatpro.com || log_warning "SSL certificate setup failed - DNS may not be configured yet"
fi

# Setup monitoring (optional)
read -p "Setup basic monitoring? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Setting up basic monitoring..."
    sudo apt install -y prometheus-node-exporter
    sudo systemctl enable prometheus-node-exporter
    sudo systemctl start prometheus-node-exporter
    log_success "Basic monitoring setup"
fi

# Create systemd service for the application
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/bdchatpro.service > /dev/null <<EOF
[Unit]
Description=Bangla AI Platform
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/bdchatpro
User=$USER
ExecStart=/bin/bash -c "echo 'Application started - manual management required'"
ExecStop=/bin/bash -c "echo 'Application stopped - manual management required'"
ExecReload=/bin/bash -c "echo 'Application reload - manual management required'"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable bdchatpro
log_success "Systemd service created"

# Setup backup script (basic)
log_info "Setting up basic backup script..."
sudo tee /opt/bdchatpro/backup.sh > /dev/null <<EOF
#!/bin/bash
# Basic backup script for bdchatpro.com
BACKUP_DIR="/opt/bdchatpro/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Note: Database backup requires manual setup without Docker
echo "Database backup requires manual configuration - no Docker available"
echo "Please configure PostgreSQL backup manually"

# Backup environment file
cp /opt/bdchatpro/.env \$BACKUP_DIR/env_backup_\$DATE

# Compress old backups (keep last 7 days)
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "env_backup_*" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

sudo chmod +x /opt/bdchatpro/backup.sh

# Setup cron job for backups
(crontab -l ; echo "0 2 * * * /opt/bdchatpro/backup.sh") | crontab -
log_success "Backup script configured (daily at 2 AM)"

log_success "🎉 VPS setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Configure DNS: Run ./deploy/setup-dns.sh for DNS commands"
echo "2. Setup SSL: sudo certbot --nginx -d bdchatpro.com -d www.bdchatpro.com"
echo "3. Configure environment: cp deploy/env.prod .env and edit secrets"
echo "4. Deploy application: ./deploy/deploy.sh"
echo "5. Test deployment: curl https://bdchatpro.com/health"
echo ""
echo "🔐 Security reminders:"
echo "• Change default passwords in .env"
echo "• Setup SSH key authentication only"
echo "• Regularly update the system"
echo "• Monitor logs: sudo journalctl -u bdchatpro -f"
echo ""
echo "📊 Monitoring:"
echo "• Application logs: Check /opt/bdchatpro/logs/ directory"
echo "• Nginx logs: sudo tail -f /var/log/nginx/bdchatpro.access.log"
echo "• System monitoring: htop or sudo systemctl status bdchatpro"
echo ""
echo "🆘 Troubleshooting:"
echo "• Restart services: sudo systemctl restart bdchatpro"
echo "• View service status: sudo systemctl status bdchatpro"
echo "• Check application status: ps aux | grep python"
echo "• View application logs: tail -f /opt/bdchatpro/logs/*.log"
