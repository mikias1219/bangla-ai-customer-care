#!/usr/bin/env bash
set -euo pipefail

# Health Check Script for bdchatpro.com
# This script performs comprehensive health checks for the production deployment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${DOMAIN:-bdchatpro.com}"
API_BASE="${API_BASE:-https://$DOMAIN}"
DASHBOARD_URL="${DASHBOARD_URL:-https://$DOMAIN}"

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

# Health check results
CHECKS_PASSED=0
CHECKS_FAILED=0
TOTAL_CHECKS=0

check_result() {
    local name="$1"
    local status="$2"
    local message="$3"

    ((TOTAL_CHECKS++))

    if [ "$status" -eq 0 ]; then
        log_success "✓ $name: $message"
        ((CHECKS_PASSED++))
    else
        log_error "✗ $name: $message"
        ((CHECKS_FAILED++))
    fi
}

log_info "🏥 Health Check for $DOMAIN"
echo "================================="

# Check DNS resolution
log_info "Checking DNS resolution..."
if nslookup $DOMAIN > /dev/null 2>&1; then
    check_result "DNS Resolution" 0 "$DOMAIN resolves correctly"
else
    check_result "DNS Resolution" 1 "$DOMAIN DNS resolution failed"
fi

# Check SSL certificate
log_info "Checking SSL certificate..."
if openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null > /dev/null 2>&1; then
    # Check certificate expiry (more than 30 days)
    if openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -checkend 2592000 > /dev/null 2>&1; then
        check_result "SSL Certificate" 0 "Valid SSL certificate (expires in >30 days)"
    else
        check_result "SSL Certificate" 1 "SSL certificate expires soon (<30 days)"
    fi
else
    check_result "SSL Certificate" 1 "SSL certificate not accessible"
fi

# Check HTTP to HTTPS redirect
log_info "Checking HTTP redirect..."
if curl -s -I http://$DOMAIN | grep -i "location: https://" > /dev/null; then
    check_result "HTTP Redirect" 0 "HTTP redirects to HTTPS correctly"
else
    check_result "HTTP Redirect" 1 "HTTP does not redirect to HTTPS"
fi

# Check dashboard accessibility
log_info "Checking dashboard accessibility..."
if curl -f -s -I $DASHBOARD_URL > /dev/null; then
    check_result "Dashboard Access" 0 "Dashboard is accessible"
else
    check_result "Dashboard Access" 1 "Dashboard is not accessible"
fi

# Check API health endpoint
log_info "Checking API health..."
if curl -f -s $API_BASE/health > /dev/null; then
    check_result "API Health" 0 "API health check passed"
else
    check_result "API Health" 1 "API health check failed"
fi

# Check API docs
log_info "Checking API documentation..."
if curl -f -s $API_BASE/docs > /dev/null; then
    check_result "API Docs" 0 "API documentation accessible"
else
    check_result "API Docs" 1 "API documentation not accessible"
fi

# Check Docker services
log_info "Checking Docker services..."
if command -v docker &> /dev/null && docker compose -f deploy/docker-compose.prod.yml ps --quiet | grep -q .; then
    running_services=$(docker compose -f deploy/docker-compose.prod.yml ps --services --filter "status=running" | wc -l)
    total_services=$(docker compose -f deploy/docker-compose.prod.yml ps --services | wc -l)

    if [ "$running_services" -eq "$total_services" ]; then
        check_result "Docker Services" 0 "All $total_services services running"
    else
        check_result "Docker Services" 1 "$running_services/$total_services services running"
    fi
else
    check_result "Docker Services" 1 "Cannot check Docker services"
fi

# Check database connectivity (if backend is running)
log_info "Checking database connectivity..."
if docker compose -f deploy/docker-compose.prod.yml exec -T backend python -c "
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

try:
    engine = create_engine(os.getenv('BANG_DATABASE_URL'))
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    check_result "Database" 0 "Database connection successful"
else
    check_result "Database" 1 "Database connection failed"
fi

# Check Redis connectivity
log_info "Checking Redis connectivity..."
if docker compose -f deploy/docker-compose.prod.yml exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    check_result "Redis" 0 "Redis connection successful"
else
    check_result "Redis" 1 "Redis connection failed"
fi

# Check system resources
log_info "Checking system resources..."
cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')

if (( $(echo "$cpu_usage < 90" | bc -l) )); then
    check_result "CPU Usage" 0 "CPU usage: ${cpu_usage}%"
else
    check_result "CPU Usage" 1 "High CPU usage: ${cpu_usage}%"
fi

if (( $(echo "$mem_usage < 90" | bc -l) )); then
    check_result "Memory Usage" 0 "Memory usage: ${mem_usage}%"
else
    check_result "Memory Usage" 1 "High memory usage: ${mem_usage}%"
fi

# Check disk space
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 90 ]; then
    check_result "Disk Space" 0 "Disk usage: ${disk_usage}%"
else
    check_result "Disk Space" 1 "Low disk space: ${disk_usage}%"
fi

# Check SSL rating (basic)
log_info "Checking SSL security..."
ssl_cipher=$(openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -text | grep "Signature Algorithm" | head -1)
if echo "$ssl_cipher" | grep -q "sha256"; then
    check_result "SSL Security" 0 "Modern SSL configuration"
else
    check_result "SSL Security" 1 "Outdated SSL configuration"
fi

# Summary
echo ""
echo "📊 Health Check Summary"
echo "======================="
echo "Total Checks: $TOTAL_CHECKS"
echo "Passed: $CHECKS_PASSED"
echo "Failed: $CHECKS_FAILED"

if [ "$CHECKS_FAILED" -eq 0 ]; then
    log_success "🎉 All health checks passed! Your application is healthy."
    exit 0
else
    log_error "❌ $CHECKS_FAILED health checks failed. Please investigate."
    echo ""
    echo "🔧 Troubleshooting Tips:"
    echo "• Check Docker logs: docker compose -f deploy/docker-compose.prod.yml logs -f"
    echo "• Check Nginx logs: sudo tail -f /var/log/nginx/bdchatpro.access.log"
    echo "• Restart services: docker compose -f deploy/docker-compose.prod.yml restart"
    echo "• Check system resources: htop"
    echo "• Test individual endpoints manually"
    exit 1
fi
