#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Domains to test
DOMAINS=("bdchatpro.com" "api.bdchatpro.com")
TIMEOUT=10

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

test_endpoint() {
    local url="$1"
    local expected_code="${2:-200}"
    local description="$3"

    echo -n "Testing $description ($url)... "

    if response=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" --max-time $TIMEOUT "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://' | sed -e 's/;TIME:.*//g')
        time_taken=$(echo "$response" | tr -d '\n' | sed -e 's/.*TIME://')

        if [ "$http_code" = "$expected_code" ]; then
            log_success "✓ $description - HTTP $http_code (${time_taken}s)"
        else
            log_warning "⚠ $description - HTTP $http_code (expected $expected_code, ${time_taken}s)"
        fi
    else
        log_error "✗ $description - Failed to connect"
    fi
}

echo "🧪 Testing Deployed Domains for Bangla AI Platform"
echo "=================================================="

# Test DNS resolution
echo ""
log_info "Testing DNS Resolution:"
for domain in "${DOMAINS[@]}"; do
    if nslookup "$domain" >/dev/null 2>&1; then
        ip=$(nslookup "$domain" 2>/dev/null | grep -A1 "Name:" | grep "Address:" | head -1 | awk '{print $2}')
        log_success "✓ $domain resolves to $ip"
    else
        log_error "✗ $domain DNS resolution failed"
    fi
done

# Test HTTP endpoints
echo ""
log_info "Testing HTTP Endpoints:"

# Main domain
test_endpoint "http://bdchatpro.com/" "200" "Main Dashboard"
test_endpoint "http://bdchatpro.com/health" "200" "Health Check"
test_endpoint "http://bdchatpro.com/api/health" "200" "API Health"
test_endpoint "http://bdchatpro.com/docs" "200" "API Docs"

# API subdomain
if nslookup "api.bdchatpro.com" >/dev/null 2>&1; then
    test_endpoint "http://api.bdchatpro.com/" "200" "API Subdomain"
    test_endpoint "http://api.bdchatpro.com/health" "200" "API Subdomain Health"
else
    log_warning "⚠ api.bdchatpro.com not configured (DNS not resolving)"
fi

# Test HTTPS (SSL)
echo ""
log_info "Testing HTTPS/SSL:"

# Main domain HTTPS
if curl -s --max-time $TIMEOUT -I "https://bdchatpro.com/" >/dev/null 2>&1; then
    log_success "✓ bdchatpro.com HTTPS accessible"
else
    log_error "✗ bdchatpro.com HTTPS failed (SSL/certificate issue)"
fi

# API subdomain HTTPS
if nslookup "api.bdchatpro.com" >/dev/null 2>&1; then
    if curl -s --max-time $TIMEOUT -I "https://api.bdchatpro.com/" >/dev/null 2>&1; then
        log_success "✓ api.bdchatpro.com HTTPS accessible"
    else
        log_error "✗ api.bdchatpro.com HTTPS failed"
    fi
fi

# SSL Certificate check
echo ""
log_info "SSL Certificate Details:"
if ssl_info=$(openssl s_client -connect bdchatpro.com:443 -servername bdchatpro.com < /dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null); then
    echo "$ssl_info" | while read line; do
        echo "  $line"
    done
else
    log_error "✗ Cannot retrieve SSL certificate information"
fi

echo ""
echo "📊 Test Summary:"
echo "================"

# Check if services appear to be running
if curl -s --max-time 5 "http://bdchatpro.com/" >/dev/null 2>&1; then
    echo "✅ Main domain (bdchatpro.com) is responding"
else
    echo "❌ Main domain (bdchatpro.com) is not responding"
fi

if curl -s --max-time 5 "http://bdchatpro.com/api/health" >/dev/null 2>&1; then
    echo "✅ API appears to be running"
else
    echo "❌ API does not appear to be running"
fi

if curl -s --max-time 5 "https://bdchatpro.com/" >/dev/null 2>&1; then
    echo "✅ HTTPS is working"
else
    echo "❌ HTTPS is not working (SSL certificate issue)"
fi

echo ""
echo "🔧 Recommendations:"
echo "=================="
echo "1. Fix SSL certificate for bdchatpro.com (currently shows admin.brainwavedigitalsolution.com)"
echo "2. Deploy the actual React dashboard to replace the placeholder page"
echo "3. Ensure the FastAPI backend is running and accessible"
echo "4. Configure api.bdchatpro.com subdomain if needed"
echo "5. Run the deployment scripts: ./deploy/deploy.sh"
