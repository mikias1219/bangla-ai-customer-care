# Quick Fix for VPS Git Conflicts

## Problem
You're getting this error when pulling from GitHub:
```
error: Your local changes to the following files would be overwritten by merge
error: The following untracked working tree files would be overwritten by merge
```

## ⚡ Quick Solution

Run this command on your VPS (as root):

```bash
cd ~/bangla-ai-customer-care && \
git stash --include-untracked && \
git reset --hard HEAD && \
git clean -fd && \
git pull origin main && \
echo "✅ VPS is now ready for automated deployments!"
```

## 🔍 What This Does

1. **`git stash --include-untracked`** - Saves your local changes
2. **`git reset --hard HEAD`** - Resets all modified files
3. **`git clean -fd`** - Removes untracked files
4. **`git pull origin main`** - Pulls latest changes from GitHub

## 📋 After Running This

Your VPS will be clean and ready for automated deployments. From now on:

1. **Just push to GitHub** - The GitHub Action will automatically deploy everything
2. **No manual pulls needed** - The deployment script handles everything
3. **No conflicts** - Automated deployments overwrite files properly

## 🚀 Next Steps

After fixing the conflicts, trigger a deployment:

### Option 1: Push a new commit
```bash
# On your local machine
git add .
git commit -m "Enable automated deployment"
git push origin main
```

### Option 2: Manually trigger from GitHub
1. Go to: https://github.com/mikias1219/bangla-ai-customer-care/actions
2. Click "Deploy (VPS, no Docker)"
3. Click "Run workflow"
4. Select `main` branch
5. Click "Run workflow"

## ✅ Verify Deployment

After deployment completes, check:

```bash
# On VPS - Check if backend is running
sudo systemctl status bangla-backend

# Test API
curl http://localhost:8000/health

# Test frontend
curl -I https://bdchatpro.com
```

## 🎯 Expected Result

- ✅ https://bdchatpro.com loads your frontend
- ✅ https://bdchatpro.com/api/docs shows API documentation
- ✅ https://bdchatpro.com/health returns `{"status":"healthy"}`

---

**Need help? Check AUTOMATED_DEPLOYMENT_GUIDE.md for detailed troubleshooting.**

