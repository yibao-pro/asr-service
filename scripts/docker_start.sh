#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${SERVICE_ROOT}"

exec python -m uvicorn api.app:app \
  --host "${ASR_SERVICE_HOST:-0.0.0.0}" \
  --port "${ASR_SERVICE_PORT:-8032}"
