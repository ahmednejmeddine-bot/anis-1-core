#!/usr/bin/env bash
# ANIS-1 Production Startup Script
# Called by Replit deployment after the build step (npm run build) has completed.
#
# Starts two processes:
#   1. FastAPI backend  — 0.0.0.0:8000  (internal; Vite proxy routes /api calls here)
#   2. Vite preview     — 0.0.0.0:5000  (public entry point, serves dist/ + proxies API)
set -euo pipefail

echo "[ANIS-1] Starting FastAPI backend on 0.0.0.0:8000..."
python3 -m uvicorn api.server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 &
BACKEND_PID=$!
echo "[ANIS-1] Backend PID: $BACKEND_PID"

echo "[ANIS-1] Starting Vite preview on 0.0.0.0:5000..."
exec npm run preview
