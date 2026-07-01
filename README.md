# Bigstar Inventory Management System (BIMS)

A full-stack web-based inventory management system designed for Bigstar Optoelectronics (LED display industry).

## Quick Start - unRAID Deployment

### Option A: Using the deploy script (Recommended - no docker-compose needed)

```bash
cd /mnt/user/appdata/
git clone https://github.com/josephyong96/bigstar-bims.git
cd bigstar-bims
cp .env.example .env

# Edit .env with your passwords
nano .env

# Make script executable and run
chmod +x deploy.sh
./deploy.sh
```

### Option B: Install docker-compose first

```bash
# Install docker-compose via pip
pip install docker-compose

# Then use docker-compose
cd /mnt/user/appdata/bigstar-bims
docker-compose up -d --build
```

### Option C: Manual docker run commands

```bash
cd /mnt/user/appdata/bigstar-bims

# 1. Create network
docker network create bims-network

# 2. Start PostgreSQL
docker run -d --name bims-db --network bims-network \
  -e POSTGRES_DB=bigstar_inventory \
  -e POSTGRES_USER=bigstar \
  -e POSTGRES_PASSWORD=bigstar123 \
  -v /mnt/user/appdata/bigstar-bims/postgres_data:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:15-alpine

# 3. Build and start backend
docker build -t bims-backend ./backend/
docker run -d --name bims-backend --network bims-network \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://bigstar:bigstar123@bims-db:5432/bigstar_inventory" \
  -e SECRET_KEY="bigstar-secret-key" \
  bims-backend \
  sh -c "cd /app/app && python init_data.py && cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8000"

# 4. Build and start frontend
docker build -t bims-frontend ./frontend/
docker run -d --name bims-frontend --network bims-network \
  -p 8080:80 --restart unless-stopped \
  bims-frontend
```

## Access the Application

| URL | Description |
|-----|-------------|
| http://YOUR-UNRAID-IP:8080 | BIMS Web Application |
| http://YOUR-UNRAID-IP:8000/docs | API Documentation (Swagger UI) |

**Default Login:**
- Username: `admin`
- Password: `admin123`

## System Architecture

```
User (Browser)
    |
    v
+---------------+      +----------------+      +-----------------+
|  Frontend     | ---> |   Backend API  | ---> |   PostgreSQL    |
|  (Nginx:80)   |      |  (FastAPI:8000)|      |   (DB:5432)     |
|  Port: 8080   |      |   Port: 8000   |      |                 |
+---------------+      +----------------+      +-----------------+
```

## Features

- **Multi-Category Inventory**: Products, Raw Materials, Rental Items
- **Flexible Tracking**: Serial Number, Batch Number, or both
- **Multi-Location**: Warehouse, Repair Center, Client Sites
- **Stock Operations**: Stock In, Stock Out (with approval), Transfer
- **Purchase Orders**: Create PO, receive goods
- **Delivery Orders**: Pick, pack, ship
- **Project Management**: Allocate stock to projects
- **Repair Center**: Full repair workflow
- **Reports & Dashboard**: KPIs, low stock alerts
- **Role-Based Access**: Management, PM, Sales, Warehouse, Technician
- **Barcode/QR Code**: Generate and scan

## User Roles

| Role | Permissions |
|------|-------------|
| Management | Full access to everything |
| Project Manager | Stock out requests, project management |
| Sales | Verify stock outs, view inventory |
| Warehouse | Stock in/out, transfers, PO/DO |
| Technician | Repair tickets, spare parts |

## Management Commands

```bash
# View logs
docker logs -f bims-backend
docker logs -f bims-frontend
docker logs -f bims-db

# Restart services
docker restart bims-backend bims-frontend

# Stop all
docker stop bims-db bims-backend bims-frontend

# Remove all containers (data preserved)
docker rm bims-db bims-backend bims-frontend

# Full cleanup including database (WARNING: deletes all data!)
docker rm -f bims-db bims-backend bims-frontend
docker network rm bims-network
rm -rf /mnt/user/appdata/bigstar-bims/postgres_data
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript + Tailwind CSS |
| Backend | Python 3.11 + FastAPI + SQLAlchemy |
| Database | PostgreSQL 15 |
| Auth | JWT (bcrypt + python-jose) |
| Deployment | Docker |

## Default Data

On first startup, the system creates:
- Admin user: `admin` / `admin123`
- Default locations: Main Warehouse KL, Repair Center, Thailand Office, Thailand Warehouse
- LED-specific categories: LED Module, LED Cabinet, Controller, Power Supply, etc.

## License

Private - For Bigstar Optoelectronics (M) Sdn Bhd
