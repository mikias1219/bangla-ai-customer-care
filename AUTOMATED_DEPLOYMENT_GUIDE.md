# Automated Deployment Guide for bdchatpro.com

This guide will help you set up fully automated deployment to your VPS at **bdchatpro.com**.

## 🚀 Overview

Every time you push to the `main` branch, GitHub Actions will automatically:
1. Build the frontend dashboard
2. Deploy backend and frontend to your VPS
3. Set up/update the systemd service
4. Configure Nginx
5. Set up HTTPS with Let's Encrypt
6. Initialize the database and add sample products

## 📋 Prerequisites

### 1. VPS Requirements
- Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Domain pointing to VPS IP (bdchatpro.com)
- Ports 80 and 443 open

### 2. GitHub Secrets Configuration

Go to your repository → Settings → Secrets and variables → Actions

#### Required Secrets:
- **`OPENAI_API`** - Your OpenAI API key (already configured ✅)
- **`VPS_HOST`** - Your VPS IP or hostname (e.g., `srv596142.hstgr.cloud`)
- **`VPS_USER`** - VPS username (e.g., `root`)
- **`VPS_PATH`** - Deployment path (e.g., `/root/bangla-ai-customer-care`)
- **`VPS_SSH_KEY`** - Private SSH key for deployment

#### Optional Variables:
- **`LETSENCRYPT_EMAIL`** - Email for Let's Encrypt SSL (recommended)

## 🔧 Initial VPS Setup

### Step 1: Clean up existing conflicts

SSH into your VPS and run the cleanup script:

```bash
ssh root@srv596142.hstgr.cloud
cd ~/bangla-ai-customer-care
chmod +x deploy/vps-cleanup.sh
./deploy/vps-cleanup.sh
```

Or manually clean up:

```bash
cd ~/bangla-ai-customer-care
git stash --include-untracked
git reset --hard HEAD
git pull origin main
```

### Step 2: Verify SSH Key

Make sure your `VPS_SSH_KEY` in GitHub secrets matches a public key on your VPS:

```bash
# On your VPS, check authorized keys
cat ~/.ssh/authorized_keys

# If you need to add a new key, copy your public key to the VPS:
# On your local machine:
cat ~/.ssh/id_rsa.pub

# On VPS:
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Step 3: Verify GitHub Secrets

Make sure all secrets are properly set:

```bash
# Test SSH connection from GitHub Actions
ssh -i ~/.ssh/your_key root@srv596142.hstgr.cloud "echo 'Connection successful'"
```

## 🎯 How to Deploy

### Automatic Deployment (Recommended)

Simply push to main:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

GitHub Actions will automatically deploy to bdchatpro.com!

### Manual Deployment

Trigger manually from GitHub:
1. Go to Actions tab
2. Select "Deploy (VPS, no Docker)"
3. Click "Run workflow"
4. Select `main` branch
5. Click "Run workflow"

## 📊 Monitoring Deployment

### View Logs in GitHub Actions

1. Go to your repository → Actions
2. Click on the latest workflow run
3. View each step's logs

### Check Status on VPS

```bash
# Check backend service
sudo systemctl status bangla-backend

# View backend logs
sudo journalctl -u bangla-backend -f

# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Test API
curl http://localhost:8000/health
```

## 🔍 Troubleshooting

### Deployment Fails at "Remote deploy & restart"

**Problem**: Permission issues
```bash
# On VPS, fix ownership
sudo chown -R root:root ~/bangla-ai-customer-care
```

**Problem**: Backend service won't start
```bash
# Check logs
sudo journalctl -u bangla-backend -n 50 --no-pager

# Check if port 8000 is already in use
sudo lsof -i :8000

# Restart manually
cd ~/bangla-ai-customer-care/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### SSL Certificate Issues

**Problem**: Certbot fails
```bash
# Make sure your domain points to the VPS
dig +short bdchatpro.com

# Try manual certificate
sudo certbot --nginx -d bdchatpro.com -d www.bdchatpro.com
```

### Frontend Not Loading

**Problem**: 404 errors
```bash
# Check Nginx config
sudo nginx -t
sudo systemctl reload nginx

# Check files exist
ls -la /var/www/bangla/

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Database Not Initialized

```bash
cd ~/bangla-ai-customer-care/backend
source .venv/bin/activate
python scripts/init_db.py
python scripts/add_sample_products.py
```

## 🔐 Security Best Practices

1. **Change Default Credentials**: Update admin password after first login
2. **Use Strong SSH Keys**: Generate 4096-bit RSA keys
3. **Enable Firewall**: Use `ufw` to restrict access
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
4. **Regular Updates**: Keep system packages updated
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## 📱 Testing Your Deployment

After deployment completes:

1. **Frontend**: https://bdchatpro.com
2. **API Docs**: https://bdchatpro.com/api/docs
3. **Health Check**: https://bdchatpro.com/health
4. **Admin Panel**: https://bdchatpro.com/api/admin/intents

Default admin credentials:
- Username: `admin`
- Password: `admin123`

⚠️ **Change these immediately in production!**

## 🎉 Success Criteria

- ✅ Frontend loads at https://bdchatpro.com
- ✅ API responds at https://bdchatpro.com/api/docs
- ✅ Backend service is running: `sudo systemctl is-active bangla-backend`
- ✅ Nginx is running: `sudo systemctl is-active nginx`
- ✅ SSL certificate is installed (no browser warnings)
- ✅ Health check returns 200: `curl https://bdchatpro.com/health`

## 📞 Support

If you encounter issues:

1. Check GitHub Actions logs
2. Check VPS logs: `sudo journalctl -u bangla-backend -f`
3. Review Nginx logs: `sudo tail -f /var/log/nginx/error.log`
4. Verify DNS: `dig +short bdchatpro.com`
5. Test connectivity: `curl -I https://bdchatpro.com`

---

**Happy Deploying! 🚀**

