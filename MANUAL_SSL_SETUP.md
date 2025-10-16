# Manual SSL Certificate Installation Guide

## ✅ Good News!
The SSL certificate was successfully obtained and saved at:
- Certificate: `/etc/letsencrypt/live/bdchatpro.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/bdchatpro.com/privkey.pem`

## 🔧 Problem
Certbot couldn't automatically install it because the Nginx configuration wasn't found.

## 📋 Solution: Manual Installation

Run these commands on your VPS:

### Step 1: Check Current Nginx Configuration

```bash
# Check if bangla config exists
cat /etc/nginx/sites-available/bangla

# Check enabled sites
ls -la /etc/nginx/sites-enabled/
```

### Step 2: Create/Update Nginx Configuration

```bash
# Create the proper Nginx configuration with SSL
sudo tee /etc/nginx/sites-available/bangla > /dev/null << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name bdchatpro.com www.bdchatpro.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name bdchatpro.com www.bdchatpro.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/bdchatpro.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bdchatpro.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Frontend (React/Vue/Static files)
    location / {
        root /var/www/bangla;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Channels endpoint
    location /channels/ {
        proxy_pass http://127.0.0.1:8000/channels/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
}
EOF
```

### Step 3: Enable the Site

```bash
# Remove old symlink if exists
sudo rm -f /etc/nginx/sites-enabled/bangla

# Create new symlink
sudo ln -s /etc/nginx/sites-available/bangla /etc/nginx/sites-enabled/bangla

# Remove default site to avoid conflicts
sudo rm -f /etc/nginx/sites-enabled/default
```

### Step 4: Test and Reload Nginx

```bash
# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx

# Check Nginx status
sudo systemctl status nginx
```

### Step 5: Verify Backend is Running

```bash
# Check backend service
sudo systemctl status bangla-backend

# If not running, start it
sudo systemctl start bangla-backend

# View logs if needed
sudo journalctl -u bangla-backend -n 50 --no-pager
```

### Step 6: Test Your Website

```bash
# Test HTTP (should redirect to HTTPS)
curl -I http://bdchatpro.com

# Test HTTPS
curl -I https://bdchatpro.com

# Test API
curl https://bdchatpro.com/health

# Test backend directly
curl http://localhost:8000/health
```

## 🧪 Quick Test Commands (All in One)

```bash
# Run all these commands together
cd ~/bangla-ai-customer-care && \
sudo nginx -t && \
sudo systemctl reload nginx && \
sudo systemctl status bangla-backend --no-pager && \
echo "Testing HTTP:" && curl -I http://bdchatpro.com 2>&1 | head -5 && \
echo "Testing HTTPS:" && curl -I https://bdchatpro.com 2>&1 | head -5 && \
echo "Testing Health:" && curl https://bdchatpro.com/health
```

## ✅ Success Indicators

You should see:
- ✅ HTTP returns `301 Moved Permanently` (redirect to HTTPS)
- ✅ HTTPS returns `200 OK`
- ✅ `/health` returns `{"status":"ok"}`
- ✅ Backend service is `active (running)`
- ✅ Website loads in browser at https://bdchatpro.com

## 🔒 SSL Certificate Auto-Renewal

Certbot automatically sets up renewal. To test:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

## 🆘 Troubleshooting

### Issue: Nginx test fails
```bash
# View detailed error
sudo nginx -t

# Check syntax errors in config
cat /etc/nginx/sites-available/bangla
```

### Issue: 502 Bad Gateway
```bash
# Backend not running
sudo systemctl restart bangla-backend
sudo journalctl -u bangla-backend -f
```

### Issue: 404 Not Found
```bash
# Frontend files missing
ls -la /var/www/bangla/
# Should see index.html
```

### Issue: SSL certificate error
```bash
# Check certificate files
sudo ls -la /etc/letsencrypt/live/bdchatpro.com/

# Reinstall certificate
sudo certbot install --cert-name bdchatpro.com
```

## 📱 After Success

Your website will be accessible at:
- ✅ https://bdchatpro.com
- ✅ https://www.bdchatpro.com
- ✅ https://bdchatpro.com/api/docs (API Documentation)
- ✅ https://bdchatpro.com/health (Health Check)

All HTTP traffic will automatically redirect to HTTPS! 🔒

