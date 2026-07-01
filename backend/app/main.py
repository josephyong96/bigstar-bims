"""Bigstar Inventory Management System (BIMS) - FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.init_data import seed_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting BIMS backend...")
    try:
        init_db()
        logger.info("Database tables created")
        db = SessionLocal()
        try:
            seed_data(db)
            logger.info("Seed data initialized")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Startup error: {e}")
    yield
    logger.info("Shutting down BIMS backend...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Inventory management system for Bigstar Optoelectronics",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": exc.errors()})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Database error occurred"})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}


from app.routers import (
    auth, users, locations, categories, items, stock,
    serial_numbers, batch_numbers, purchase_orders, delivery_orders,
    projects, repair_tickets, reports, barcodes,
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(serial_numbers.router, prefix="/api/v1")
app.include_router(batch_numbers.router, prefix="/api/v1")
app.include_router(purchase_orders.router, prefix="/api/v1")
app.include_router(delivery_orders.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(repair_tickets.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(barcodes.router, prefix="/api/v1")

logger.info("BIMS routers loaded successfully")
