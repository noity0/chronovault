#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"
echo "ChronoVault 2.0 starting..."
echo "Browser: http://127.0.0.1:8765"
exec python3 chrono.py cockpit "$@"
