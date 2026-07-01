from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth, users, items, stock, locations, projects,
    purchase_orders, delivery_orders, repair_tickets,
    serial_numbers, batch_numbers, barcodes, reports
)

app = FastAPI(title="BIMS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "BIMS API is running"}

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(stock.router, prefix="/stock", tags=["Stock"])
app.include_router(locations.router, prefix="/locations", tags=["Locations"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])
app.include_router(delivery_orders.router, prefix="/delivery-orders", tags=["Delivery Orders"])
app.include_router(repair_tickets.router, prefix="/repair-tickets", tags=["Repair Tickets"])
app.include_router(serial_numbers.router, prefix="/serials", tags=["Serial Numbers"])
app.include_router(batch_numbers.router, prefix="/batches", tags=["Batch Numbers"])
app.include_router(barcodes.router, prefix="/barcodes", tags=["Barcodes"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
