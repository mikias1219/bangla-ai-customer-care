#!/usr/bin/env bash
set -euo pipefail

# Monitoring Script for bdchatpro.com
# This script provides continuous monitoring and alerting capabilities

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${DOMAIN:-bdchatpro.com}"
ALERT_EMAIL="${ALERT_EMAIL:-admin@bdchatpro.com}"
LOG_FILE="${LOG_FILE:-/opt/bdchatpro/logs/monitor.log}"
ALERT_LOG="${ALERT_LOG:-/opt/bdchatpro/logs/alerts.log}"

# Create log directories
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$ALERT_LOG")"

# Logging functions
log_info() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_alert() {
    local message="$1"
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${RED}[ALERT]${NC} $message" | tee -a "$ALERT_LOG"

    # Send email alert if mail is available
    if command -v mail &> /dev/null && [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "bdchatpro.com Alert: $(hostname)" "$ALERT_EMAIL"
    fi
}

# Monitoring state file
STATE_FILE="/tmp/bdchatpro_monitor.state"
touch "$STATE_FILE"

# Get previous state
get_state() {
    local key="$1"
    grep "^$key:" "$STATE_FILE" 2>/dev/null | cut -d: -f2- || echo ""
}

# Set state
set_state() {
    local key="$1"
    local value="$2"
    # Remove old state
    sed -i "/^$key:/d" "$STATE_FILE" 2>/dev/null || true
    # Add new state
    echo "$key:$value" >> "$STATE_FILE"
}

# Check service status
check_service() {
    local service_name="$1"
    local check_command="$2"
    local alert_message="$3"

    local previous_status
    previous_status=$(get_state "$service_name")

    if eval "$check_command" > /dev/null 2>&1; then
        if [ "$previous_status" = "failed" ]; then
            log_success "$service_name recovered"
        fi
        set_state "$service_name" "ok"
        return 0
    else
        if [ "$previous_status" != "failed" ]; then
            log_alert "$alert_message"
        fi
        set_state "$service_name" "failed"
        return 1
    fi
}

log_info "📊 Starting monitoring for $DOMAIN"

# Continuous monitoring loop
if [ "${1:-}" = "continuous" ]; then
    log_info "Running in continuous mode (press Ctrl+C to stop)"
    echo "Monitoring will run every 60 seconds..."
    echo ""

    while true; do
        run_checks
        sleep 60
    done
else
    run_checks
fi

run_checks() {
    log_info "Running monitoring checks..."

    # Check application health
    check_service "app_health" \
        "curl -f -s https://$DOMAIN/health > /dev/null" \
        "Application health check failed - https://$DOMAIN/health is not responding"

    # Check API accessibility
    check_service "api_access" \
        "curl -f -s https://$DOMAIN/docs > /dev/null" \
        "API documentation not accessible - https://$DOMAIN/docs failed"

    # Check database connectivity
    check_service "database" \
        "docker compose -f docker-compose.prod.yml exec -T backend python -c 'import os; from sqlalchemy import create_engine; engine = create_engine(os.getenv(\"BANG_DATABASE_URL\")); engine.connect().close()' 2>/dev/null" \
        "Database connectivity failed - cannot connect to PostgreSQL"

    # Check Redis connectivity
    check_service "redis" \
        "docker compose -f docker-compose.prod.yml exec -T redis redis-cli ping 2>/dev/null | grep -q PONG" \
        "Redis connectivity failed - Redis service is not responding"

    # Check SSL certificate expiry
    ssl_expiry_days=$(openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 | xargs -I {} date -d {} +%s)
    current_time=$(date +%s)
    days_until_expiry=$(( (ssl_expiry_days - current_time) / 86400 ))

    if [ "$days_until_expiry" -lt 30 ]; then
        log_alert "SSL certificate expires in $days_until_expiry days - renew immediately"
    elif [ "$days_until_expiry" -lt 7 ]; then
        log_error "SSL certificate expires in $days_until_expiry days - CRITICAL"
    fi

    # Check disk space
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log_alert "Disk usage is $disk_usage% - clean up space immediately"
    elif [ "$disk_usage" -gt 80 ]; then
        log_warning "Disk usage is $disk_usage% - monitor closely"
    fi

    # Check memory usage
    mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$mem_usage" -gt 90 ]; then
        log_alert "Memory usage is $mem_usage% - investigate memory leaks"
    fi

    # Check Docker services
    running_containers=$(docker compose -f docker-compose.prod.yml ps --services --filter "status=running" | wc -l)
    total_containers=$(docker compose -f docker-compose.prod.yml ps --services | wc -l)

    if [ "$running_containers" -ne "$total_containers" ]; then
        log_alert "$running_containers/$total_containers Docker services running - some services are down"
    fi

    # Check for error logs
    error_count=$(docker compose -f docker-compose.prod.yml logs --since 1h 2>&1 | grep -i error | wc -l)
    if [ "$error_count" -gt 10 ]; then
        log_warning "$error_count errors found in logs in the last hour"
    fi

    log_success "Monitoring checks completed"
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo ""
    echo "📋 Monitoring Usage:"
    echo "==================="
    echo "• Run once: ./deploy/monitor.sh"
    echo "• Continuous monitoring: ./deploy/monitor.sh continuous"
    echo ""
    echo "📊 Logs:"
    echo "• Monitoring log: $LOG_FILE"
    echo "• Alert log: $ALERT_LOG"
    echo ""
    echo "📧 Alerts:"
    echo "• Email alerts sent to: $ALERT_EMAIL"
    echo "• Configure ALERT_EMAIL environment variable to change"
    echo ""
    echo "🛑 To stop continuous monitoring: Ctrl+C"
    echo ""
fi

log_success "Monitoring completed"
