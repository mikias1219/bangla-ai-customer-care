#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${1:-bdchatpro.com}
APP_PATH=${2:-/opt/bangla}
WEBROOT=${3:-/var/www/bangla}

sudo apt update && sudo apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx git rsync
sudo mkdir -p "$APP_PATH" "$WEBROOT"

echo "Prepared VPS for Bangla AI at $APP_PATH with webroot $WEBROOT (domain: $DOMAIN)."


