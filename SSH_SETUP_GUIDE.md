# SSH Setup Guide for GitHub Actions Deployment

## The Problem
The GitHub Actions workflow is failing with SSH key errors. This guide will help you fix it.

## Step-by-Step Fix

### 1. Generate a New SSH Key Pair (if needed)

On your local machine or VPS:

```bash
# Generate a new SSH key specifically for deployment
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/bangla_deploy -N ""

# This creates two files:
# - ~/.ssh/bangla_deploy (private key) - for GitHub secret
# - ~/.ssh/bangla_deploy.pub (public key) - for VPS
```

### 2. Add Public Key to Your VPS

```bash
# Copy the public key to your VPS
ssh-copy-id -i ~/.ssh/bangla_deploy.pub your-username@your-vps-ip

# Or manually:
cat ~/.ssh/bangla_deploy.pub
# Copy the output, then on VPS:
# echo "paste-public-key-here" >> ~/.ssh/authorized_keys
```

### 3. Test SSH Connection

```bash
# Test that the key works
ssh -i ~/.ssh/bangla_deploy your-username@your-vps-ip "echo 'SSH works!'"
```

### 4. Add Private Key to GitHub Secrets

**IMPORTANT**: Copy the private key EXACTLY as shown below:

```bash
# Display the private key
cat ~/.ssh/bangla_deploy

# It should look like:
# -----BEGIN OPENSSH PRIVATE KEY-----
# b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtz
# ... many lines ...
# -----END OPENSSH PRIVATE KEY-----
```

**Copy the ENTIRE output** including the BEGIN and END lines.

### 5. Update GitHub Secret

1. Go to: https://github.com/YOUR-USERNAME/bangla-ai-customer-care/settings/secrets/actions
2. Click on `VPS_SSH_KEY` to edit it
3. **Delete the old value completely**
4. Paste the entire private key (from step 4)
5. Make sure there are NO extra spaces or blank lines at the start or end
6. Click "Update secret"

### 6. Verify Other Secrets

Make sure these secrets are also set correctly:

- **VPS_HOST**: Your VPS IP address or domain (e.g., `123.456.789.0` or `vps.yourdomain.com`)
- **VPS_USER**: SSH username (e.g., `root` or `ubuntu`)
- **VPS_PATH**: Deployment path (e.g., `/opt/bangla`)
- **OPENAI_API_KEY**: Your OpenAI API key (already set ✓)

### 7. Optional: Add LETSENCRYPT_EMAIL for HTTPS

1. Go to: https://github.com/YOUR-USERNAME/bangla-ai-customer-care/settings/variables/actions
2. Click "New repository variable"
3. Name: `LETSENCRYPT_EMAIL`
4. Value: `your-email@example.com`
5. Click "Add variable"

## Troubleshooting

### If SSH still fails:

**Check 1: Key format**
The private key MUST be in OpenSSH format (not PEM). If it starts with:
- `-----BEGIN RSA PRIVATE KEY-----` ← Old PEM format (convert it)
- `-----BEGIN OPENSSH PRIVATE KEY-----` ← Correct ✓

To convert if needed:
```bash
ssh-keygen -p -f ~/.ssh/bangla_deploy -m PEM -P "" -N ""
```

**Check 2: VPS SSH Configuration**

SSH to your VPS and check:
```bash
# Check SSH config allows key auth
sudo cat /etc/ssh/sshd_config | grep -i pubkey
# Should show: PubkeyAuthentication yes

# Check authorized_keys permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Restart SSH if you made changes
sudo systemctl restart sshd
```

**Check 3: GitHub Actions Logs**

The workflow now shows debug output:
- "Key begins with: ..." (should show `-----BEGIN OPENSSH PRIVATE KEY-----`)
- "Key ends with: ..." (should show `-----END OPENSSH PRIVATE KEY-----`)

If these don't match, the secret wasn't copied correctly.

## Quick Test After Fixing

1. Update the `VPS_SSH_KEY` secret as described above
2. Go to: https://github.com/YOUR-USERNAME/bangla-ai-customer-care/actions
3. Click "Re-run jobs" on the latest failed workflow
4. Watch the "Prepare SSH" step output for the debug info

## Alternative: Use GitHub Secrets in a Different Format

If you continue to have issues, you can also try base64 encoding:

```bash
# Encode the key
cat ~/.ssh/bangla_deploy | base64 -w 0

# Copy the output to GitHub secret as VPS_SSH_KEY_BASE64
```

Then update the workflow to decode it (let me know if you need this approach).

## Need Help?

If you're still stuck, share:
1. What the "Key begins with" line shows in the GitHub Actions log
2. Whether you can SSH manually from your machine
3. The output of `ls -la ~/.ssh` on your VPS

