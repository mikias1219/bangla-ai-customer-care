# SSH Key Setup Guide for GitHub Actions Deployment

## Problem
The deployment workflow is failing with "Permission denied (publickey)" because the SSH key in GitHub secrets is not properly formatted or configured.

## Solution: Step-by-Step Guide

### Step 1: Generate a New SSH Key on Your VPS

SSH into your VPS and run:

```bash
# Generate a new SSH key pair specifically for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy -N ""
```

This creates:
- **Private key**: `~/.ssh/github_actions_deploy`
- **Public key**: `~/.ssh/github_actions_deploy.pub`

### Step 2: Add Public Key to VPS authorized_keys

```bash
# Add the public key to authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Step 3: Get the Private Key

```bash
# Display the private key (you'll copy this to GitHub)
cat ~/.ssh/github_actions_deploy
```

**IMPORTANT**: The output should look like this:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...multiple lines...
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
-----END OPENSSH PRIVATE KEY-----
```

### Step 4: Add to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `VPS_SSH_KEY`
5. Value: **Paste the ENTIRE private key output** including:
   - `-----BEGIN OPENSSH PRIVATE KEY-----`
   - All the content in between
   - `-----END OPENSSH PRIVATE KEY-----`
6. Click **Add secret**

### Step 5: Verify Other Required Secrets

Make sure these secrets/variables are set:

**Secrets** (Settings → Secrets and variables → Actions → Secrets):
- `VPS_SSH_KEY` - The private key you just created
- `VPS_HOST` - Your VPS IP address (e.g., `123.45.67.89`)
- `VPS_USER` - Your VPS username (e.g., `root` or `ubuntu`)
- `VPS_PATH` - Deploy path (e.g., `/opt/bangla`)
- `OPENAI_API_KEY` - Your OpenAI API key

**Variables** (Settings → Secrets and variables → Actions → Variables):
- `LETSENCRYPT_EMAIL` - Your email for SSL certificate (optional)

### Step 6: Test the Connection

Test the SSH connection from your local machine:

```bash
# Download the private key temporarily to test
scp your-vps-user@your-vps-ip:~/.ssh/github_actions_deploy /tmp/test_key
chmod 600 /tmp/test_key

# Test connection
ssh -i /tmp/test_key your-vps-user@your-vps-ip "echo 'Connection successful!'"

# Clean up
rm /tmp/test_key
```

If this works, GitHub Actions will also work.

### Step 7: Push to Trigger Deployment

```bash
git add .
git commit -m "Update deployment workflow with SSH key fix"
git push origin main
```

## Troubleshooting

### Error: "Load key: invalid format"
- **Cause**: The private key was not copied correctly to GitHub secrets
- **Fix**: Make sure you copied the ENTIRE key including the BEGIN and END lines

### Error: "Permission denied (publickey)"
- **Cause**: Public key not in authorized_keys or wrong user
- **Fix**: Verify the public key is in `~/.ssh/authorized_keys` on the VPS

### Error: "Connection refused"
- **Cause**: SSH service not running or firewall blocking
- **Fix**: Check `sudo systemctl status sshd` and firewall rules

### Error: "Host key verification failed"
- **Cause**: VPS host key not in known_hosts
- **Fix**: The workflow now uses `ssh-keyscan` to automatically add the host key

## Alternative: Use Existing SSH Key

If you already have an SSH key on your VPS:

```bash
# Find existing keys
ls -la ~/.ssh/

# Use an existing key (e.g., id_rsa or id_ed25519)
cat ~/.ssh/id_rsa  # or id_ed25519
```

Then add that private key to GitHub secrets as `VPS_SSH_KEY`.

## Security Notes

1. **Never** commit private keys to the repository
2. The private key in GitHub secrets is encrypted and only accessible during workflow runs
3. Use a dedicated key for deployments (not your personal SSH key)
4. Regularly rotate deployment keys
5. Consider using SSH key passphrases for additional security (requires workflow updates)

## What the Workflow Does

The updated workflow now:
1. Creates `~/.ssh/deploy_key` from the `VPS_SSH_KEY` secret
2. Sets correct permissions (600)
3. Uses `-i ~/.ssh/deploy_key` for all SSH/rsync commands
4. Tests the connection before proceeding
5. Adds the VPS to known_hosts automatically

This ensures consistent and secure SSH authentication throughout the deployment process.

