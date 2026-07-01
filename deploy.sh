#!/bin/bash
PORT="${1:-99}"
DATA_DIR="${2:-/mnt/user/appdata/bims-data}"

echo "========================================"
echo "  BIMS - Fresh Deploy"
echo "========================================"
echo "Port: $PORT"
echo "Data directory: $DATA_DIR"
echo ""

echo "[1/4] Stopping old container..."
docker stop bims 2>/dev/null
docker rm bims 2>/dev/null

echo "[2/4] Creating data directory..."
mkdir -p "$DATA_DIR"

echo "[3/4] Building Docker image..."
cd "$(dirname "$0")"
docker build -t bims:latest .

echo "[4/4] Starting BIMS container..."
docker run -d \
  --name bims \
  --restart unless-stopped \
  -p "${PORT}:8000" \
  -v "${DATA_DIR}:/data" \
  -e SECRET_KEY="bigstar-bims-secret-key-2024-change-in-production" \
  bims:latest

echo ""
echo "BIMS is starting up!"
echo "URL: http://your-unraid-ip:${PORT}"
echo ""
echo "Default login:"
echo "  admin / admin123"
echo "  warehouse / admin123"
echo "  sales / admin123"
echo "  pm / admin123"
echo "  tech / admin123"
echo ""
sleep 3
docker logs bims --tail 20
