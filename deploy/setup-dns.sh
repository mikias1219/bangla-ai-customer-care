#!/usr/bin/env bash
set -euo pipefail

# DNS Setup Script for bdchatpro.com
# Run this script to get DNS configuration commands for your domain

echo "🌐 DNS Configuration for bdchatpro.com"
echo "======================================"
echo ""

# Get VPS IP from user or detect
if [ -n "${VPS_IP:-}" ]; then
    IP="$VPS_IP"
else
    echo "Enter your VPS public IP address:"
    read -r IP
fi

echo "📋 DNS Records to configure for bdchatpro.com:"
echo ""
echo "1. A Records (Point domain to your VPS IP: $IP)"
echo "   • bdchatpro.com → $IP"
echo "   • www.bdchatpro.com → $IP"
echo "   • api.bdchatpro.com → $IP (optional - for separate API subdomain)"
echo ""

echo "2. CNAME Records (if using CDN like Cloudflare)"
echo "   • www → bdchatpro.com"
echo ""

echo "3. MX Records (for email - optional)"
echo "   • bdchatpro.com → mail.bdchatpro.com (priority: 10)"
echo ""

echo "4. TXT Records (for verification and security)"
echo "   • _dmarc → \"v=DMARC1; p=none; rua=mailto:dmarc@bdchatpro.com\""
echo "   • google-site-verification → your-google-verification-code (if using Google services)"
echo ""

echo "🔧 Commands to run with your DNS provider:"
echo ""

if command -v curl &> /dev/null; then
    echo "# Using curl to check current DNS (optional)"
    echo "curl -s \"https://dns.google/resolve?name=bdchatpro.com&type=A\" | jq .Answer[].data 2>/dev/null || echo 'DNS not configured yet'"
    echo ""
fi

echo "# Popular DNS providers configuration:"
echo ""
echo "# 1. Cloudflare:"
echo "#    - Go to https://dash.cloudflare.com"
echo "#    - Add site: bdchatpro.com"
echo "#    - Change nameservers to Cloudflare's nameservers"
echo "#    - Add A record: bdchatpro.com → $IP (DNS Only or Proxied)"
echo "#    - Add CNAME: www → bdchatpro.com"
echo ""
echo "# 2. Namecheap/Domain Registrar:"
echo "#    - Login to your domain registrar"
echo "#    - Go to DNS settings for bdchatpro.com"
echo "#    - Add A record: @ → $IP"
echo "#    - Add A record: www → $IP"
echo "#    - Add A record: api → $IP (optional)"
echo ""
echo "# 3. AWS Route 53 (if using AWS):"
echo "#    aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{"
echo "#      \"Changes\": [{"
echo "#        \"Action\": \"CREATE\","
echo "#        \"ResourceRecordSet\": {"
echo "#          \"Name\": \"bdchatpro.com.\","
echo "#          \"Type\": \"A\","
echo "#          \"TTL\": 300,"
echo "#          \"ResourceRecords\": [{\"Value\": \"$IP\"}]"
echo "#        }"
echo "#      }]"
echo "#    }'"
echo ""
echo "# 4. DigitalOcean DNS:"
echo "#    doctl compute domain create bdchatpro.com"
echo "#    doctl compute domain records create bdchatpro.com --record-type A --record-name @ --record-data $IP"
echo "#    doctl compute domain records create bdchatpro.com --record-type CNAME --record-name www --record-data bdchatpro.com."
echo ""

echo "⏳ DNS Propagation Time:"
echo "   • Changes may take 24-48 hours to propagate globally"
echo "   • You can check propagation at: https://dnschecker.org/"
echo ""

echo "🧪 Testing DNS Configuration:"
echo ""
echo "# Test A record resolution:"
echo "nslookup bdchatpro.com"
echo "dig bdchatpro.com A"
echo ""
echo "# Test SSL certificate (after DNS propagates):"
echo "openssl s_client -connect bdchatpro.com:443 -servername bdchatpro.com < /dev/null"
echo ""
echo "# Test application:"
echo "curl -I https://bdchatpro.com"
echo "curl https://bdchatpro.com/health"
echo ""

echo "📧 Email Configuration (Optional):"
echo ""
echo "If you want to set up email for bdchatpro.com:"
echo ""
echo "# Using Zoho Mail:"
echo "# 1. Sign up at https://www.zoho.com/mail/"
echo "# 2. Add MX records:"
echo "#    - bdchatpro.com → mx.zoho.com (priority: 10)"
echo "#    - bdchatpro.com → mx2.zoho.com (priority: 20)"
echo "#    - bdchatpro.com → mx3.zoho.com (priority: 50)"
echo ""
echo "# Using Google Workspace:"
echo "# 1. Sign up at https://workspace.google.com/"
echo "# 2. Add MX records as provided by Google"
echo ""

echo "✅ After DNS configuration:"
echo "1. Wait for propagation (check with dnschecker.org)"
echo "2. Run SSL certificate setup: ./setup-ssl.sh"
echo "3. Deploy application: ./deploy.sh"
echo "4. Test application: curl https://bdchatpro.com/health"
echo ""

echo "🆘 Troubleshooting:"
echo ""
echo "# Check DNS resolution:"
echo "dig bdchatpro.com @8.8.8.8"
echo ""
echo "# Check SSL certificate:"
echo "openssl s_client -connect bdchatpro.com:443 -servername bdchatpro.com"
echo ""
echo "# Check application logs:"
echo "docker compose -f docker-compose.prod.yml logs -f"
echo ""

echo "🎉 DNS setup commands generated for bdchatpro.com!"
