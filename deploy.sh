#!/bin/bash
# BIMS Deployment Script for unRAID (without docker-compose)
# Run this script to start all BIMS services

set -e

echo "========================================"
echo "  BIMS - Bigstar Inventory Management"
echo "  Deployment Script for unRAID"
echo "========================================"

# Configuration
DB_PASSWORD="${DB_PASSWORD:-bigstar123}"
SECRET_KEY="${SECRET_KEY:-bigstar-secret-key-change-in-production}"
NETWORK_NAME="bims-network"

cd "$(dirname "$0")"

# Load .env if exists
if [ -f .env ]; then
    echo "Loading .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Create network if not exists
echo "Creating Docker network..."
docker network ls | grep -q "$NETWORK_NAME" || docker network create "$NETWORK_NAME"

# Stop existing containers
echo "Stopping existing containers..."
docker stop bims-db bims-backend bims-frontend 2>/dev/null || true
docker rm bims-db bims-backend bims-frontend 2>/dev/null || true

# Pull and start PostgreSQL
echo "Starting PostgreSQL database..."
docker run -d \
    --name bims-db \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -e POSTGRES_DB=bigstar_inventory \
    -e POSTGRES_USER=bigstar \
    -e POSTGRES_PASSWORD="$DB_PASSWORD" \
    -v /mnt/user/appdata/bigstar-bims/postgres_data:/var/lib/postgresql/data \
    --health-cmd="pg_isready -U bigstar -d bigstar_inventory" \
    --health-interval=10s \
    --health-timeout=5s \
    --health-retries=5 \
    postgres:15-alpine

# Wait for DB to be ready
echo "Waiting for database to be ready..."
sleep 10
until docker exec bims-db pg_isready -U bigstar -d bigstar_inventory > /dev/null 2>&1; do
    echo "  Waiting for PostgreSQL..."
    sleep 2
done
echo "Database is ready!"

# Build backend image
echo "Building backend image..."
docker build -t bims-backend:latest ./backend/

# Start backend
echo "Starting backend API server..."
docker run -d \
    --name bims-backend \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 8000:8000 \
    -e DATABASE_URL="postgresql://bigstar:${DB_PASSWORD}@bims-db:5432/bigstar_inventory" \
    -e SECRET_KEY="$SECRET_KEY" \
    -e ALLOWED_ORIGINS="*" \
    -e PYTHONUNBUFFERED=1 \
    bims-backend:latest \
    sh -c "cd /app/app && python init_data.py && cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Build frontend image
echo "Building frontend image..."
docker build -t bims-frontend:latest ./frontend/

# Start frontend
echo "Starting frontend web server..."
docker run -d \
    --name bims-frontend \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 8080:80 \
    bims-frontend:latest

echo ""
echo "========================================"
echo "  BIMS Deployment Complete!"
echo "========================================"
echo ""
echo "Access your system:"
echo "  Web App:    http://YOUR-UNRAID-IP:8080"
echo "  API Docs:   http://YOUR-UNRAID-IP:8000/docs"
echo ""
echo "Default Login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "To view logs:"
echo "  Backend:  docker logs -f bims-backend"
echo "  Frontend: docker logs -f bims-frontend"
echo "  Database: docker logs -f bims-db"
echo ""
echo "To stop:"
echo "  docker stop bims-db bims-backend bims-frontend"
echo ""
