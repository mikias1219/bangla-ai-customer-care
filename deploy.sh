#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec bash deploy/deploy.sh
