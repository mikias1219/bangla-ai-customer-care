# GitHub Actions Deployment

This repository includes automated deployment using GitHub Actions for the Bangla AI Customer Care system.

## 🚀 Deployment Overview

The deployment workflow automatically:
- ✅ Sets up frontend server on port 3002
- ✅ Sets up backend API on port 8000
- ✅ Creates SSL certificates for bdchatpro.com
- ✅ Configures Nginx with proper proxy settings
- ✅ Restarts all services

## 🔧 Required GitHub Secrets

Add these secrets to your GitHub repository settings:

### Required Secrets:
- `VPS_HOST`: Your VPS IP address (e.g., `88.222.245.41`)
- `VPS_USER`: SSH username for your VPS (e.g., `root`)
- `SSH_PRIVATE_KEY`: Private SSH key for connecting to your VPS
- `SSL_EMAIL`: Email address for SSL certificate (e.g., `admin@bdchatpro.com`)
- `OPENAI_API_KEY`: Your OpenAI API key for the backend

### How to Add Secrets:
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed above

### SSH Key Setup:
```bash
# Generate SSH key pair (on your local machine)
ssh-keygen -t rsa -b 4096 -C "github-actions@your-repo"

# Copy public key to your VPS
ssh-copy-id user@your-vps-ip

# Add private key to GitHub secrets as SSH_PRIVATE_KEY
cat ~/.ssh/id_rsa
```

## 🔄 Deployment Trigger

The workflow runs automatically when:
- ✅ Code is pushed to `main` or `master` branch
- ✅ Manual trigger via GitHub Actions UI

## 📊 Services Configuration

After deployment, your services will be available at:

- **Frontend**: `https://bdchatpro.com` (served on port 3002)
- **Backend API**: `https://bdchatpro.com/api/*` (proxied to port 8000)
- **Health Check**: `https://bdchatpro.com/health`
- **WebSocket**: `https://bdchatpro.com/channels/*`

## 🔒 SSL Certificate

- **Domain**: `bdchatpro.com` and `www.bdchatpro.com`
- **Provider**: Let's Encrypt
- **Auto-renewal**: Handled by certbot

## 🛠️ Manual Deployment (Alternative)

If you prefer manual deployment, see the deployment scripts in the `deploy/` directory.

## 📝 Troubleshooting

### Common Issues:

1. **SSH Connection Failed**
   - Verify `VPS_HOST` and `VPS_USER` secrets
   - Ensure SSH key is correctly formatted in `SSH_PRIVATE_KEY`

2. **SSL Certificate Failed**
   - Verify `SSL_EMAIL` is valid
   - Ensure DNS points to your VPS IP
   - Check firewall allows port 80/443

3. **Services Not Starting**
   - Check VPS has sufficient resources
   - Verify Node.js and Python are installed

### Logs:
Check deployment logs in GitHub Actions → Your workflow → View logs

## 🎯 Success Indicators

Deployment is successful when:
- ✅ Workflow completes without errors
- ✅ `https://bdchatpro.com` loads your frontend
- ✅ `https://bdchatpro.com/health` returns `{"status":"ok"}`
- ✅ `https://bdchatpro.com/api/docs` shows FastAPI documentation
