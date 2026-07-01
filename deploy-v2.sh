#!/bin/bash
set -e
echo "========================================"
echo "  BIMS v2 - Deployment"
echo "========================================"
DB_PASSWORD="${DB_PASSWORD:-bigstar123}"
SECRET_KEY="${SECRET_KEY:-bigstar-secret-key-change-in-production}"
FRONTEND_PORT="${FRONTEND_PORT:-99}"
NETWORK_NAME="bims-network"
cd "$(dirname "$0")"
[ -f .env ] && export $(grep -v '^#' .env | xargs)

echo "[1/5] Creating network..."
docker network ls | grep -q "$NETWORK_NAME" || docker network create "$NETWORK_NAME"

echo "[2/5] Stopping old containers..."
docker stop bims-db bims-backend bims-frontend 2>/dev/null || true
docker rm bims-db bims-backend bims-frontend 2>/dev/null || true

echo "[3/5] Starting PostgreSQL..."
docker run -d --name bims-db --network "$NETWORK_NAME" --restart unless-stopped \
  -e POSTGRES_DB=bigstar_inventory -e POSTGRES_USER=bigstar \
  -e POSTGRES_PASSWORD="$DB_PASSWORD" \
  -v /mnt/user/appdata/bigstar-bims/postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

echo "  Waiting for DB..."
sleep 10
until docker exec bims-db pg_isready -U bigstar -d bigstar_inventory >/dev/null 2>&1; do
  echo "  Waiting..."; sleep 2
done
echo "  DB ready!"

echo "[4/5] Building backend v2..."
docker build -t bims-backend:v2 ./backend-v2/
docker run -d --name bims-backend --network "$NETWORK_NAME" --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://bigstar:${DB_PASSWORD}@bims-db:5432/bigstar_inventory" \
  -e SECRET_KEY="$SECRET_KEY" \
  bims-backend:v2

echo "  Waiting for backend..."
sleep 12
if docker ps | grep -q "bims-backend.*Up"; then
  echo "  Backend is UP!"
else
  echo "  Backend failed! Logs:"
  docker logs bims-backend --tail 30
  exit 1
fi

echo "[5/5] Starting frontend on port $FRONTEND_PORT..."
docker run -d --name bims-frontend --network "$NETWORK_NAME" --restart unless-stopped \
  -p "${FRONTEND_PORT}:80" bims-frontend-lite:latest 2>/dev/null || \
docker run -d --name bims-frontend --network "$NETWORK_NAME" --restart unless-stopped \
  -p "${FRONTEND_PORT}:80" bims-frontend:latest

echo ""
echo "========================================"
echo "  BIMS v2 Ready!"
echo "========================================"
echo "Web App:  http://YOUR-UNRAID-IP:${FRONTEND_PORT}"
echo "API Docs: http://YOUR-UNRAID-IP:8000/docs"
echo "Login:    admin / admin123"
echo ""
