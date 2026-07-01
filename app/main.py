"""
Bigstar Inventory Management System (BIMS)
Single-file FastAPI backend with SQLite
Serves both API and frontend static files
"""

import os, hashlib, secrets, json, datetime, re
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends, Query, Request, Body, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, Boolean, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func

# Configuration
DB_PATH = os.environ.get("DB_PATH", "/data/bims.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "bigstar-bims-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Database
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="warehouse")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location_type = Column(String, default="warehouse")
    address = Column(Text, nullable=True)
    contact_person = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_type = Column(String, default="product")
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(String, default="product")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    unit = Column(String, default="pcs")
    min_stock = Column(Integer, default=0)
    unit_cost = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    track_serial = Column(Boolean, default=False)
    track_batch = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
    datasheet_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Integer, default=0)
    serial_number = Column(String, nullable=True)
    batch_number = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String, default="available")
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True, index=True)
    movement_type = Column(String, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    serial_number = Column(String, nullable=True)
    batch_number = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    from_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    to_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    reference_type = Column(String, nullable=True)
    reference_id = Column(Integer, nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="pending")
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, nullable=False)
    supplier_name = Column(String, nullable=False)
    supplier_contact = Column(String, nullable=True)
    total_amount = Column(Float, default=0.0)
    status = Column(String, default="draft")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expected_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)

class PurchaseOrderItem(Base):
    __tablename__ = "po_items"
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, default=0.0)
    received_qty = Column(Integer, default=0)

class DeliveryOrder(Base):
    __tablename__ = "delivery_orders"
    id = Column(Integer, primary_key=True, index=True)
    do_number = Column(String, unique=True, nullable=False)
    client_name = Column(String, nullable=False)
    client_address = Column(Text, nullable=True)
    client_contact = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    status = Column(String, default="draft")
    delivery_date = Column(Date, nullable=True)
    shipped_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    remarks = Column(Text, nullable=True)

class DeliveryOrderItem(Base):
    __tablename__ = "do_items"
    id = Column(Integer, primary_key=True, index=True)
    do_id = Column(Integer, ForeignKey("delivery_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    serial_number = Column(String, nullable=True)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    client_name = Column(String, nullable=True)
    status = Column(String, default="active")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    project_manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class RepairTicket(Base):
    __tablename__ = "repair_tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    serial_number = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    issue_description = Column(Text, nullable=False)
    status = Column(String, default="received")
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    remarks = Column(Text, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data

def seed_data():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin_pw = hashlib.pbkdf2_hmac("sha256", "admin123".encode(), SECRET_KEY.encode(), 100000).hex()
            db.add(User(username="admin", full_name="Administrator", password_hash=admin_pw, role="management"))
            db.add(User(username="warehouse", full_name="Warehouse Staff", password_hash=admin_pw, role="warehouse"))
            db.add(User(username="sales", full_name="Sales Staff", password_hash=admin_pw, role="sales"))
            db.add(User(username="pm", full_name="Project Manager", password_hash=admin_pw, role="pm"))
            db.add(User(username="tech", full_name="Technician", password_hash=admin_pw, role="technician"))

        if db.query(Location).count() == 0:
            db.add(Location(name="Main Warehouse", location_type="warehouse", address="Bigstar HQ"))
            db.add(Location(name="Repair Center", location_type="repair", address="Repair Facility"))
            db.add(Location(name="Thailand Office", location_type="thailand", address="Bangkok"))

        if db.query(Category).count() == 0:
            db.add(Category(name="LED Display", category_type="product"))
            db.add(Category(name="LED Module", category_type="product"))
            db.add(Category(name="LED Controller", category_type="product"))
            db.add(Category(name="Power Supply", category_type="product"))
            db.add(Category(name="LED Cabinet", category_type="product"))
            db.add(Category(name="LED Chip", category_type="raw_material"))
            db.add(Category(name="PCB Board", category_type="raw_material"))
            db.add(Category(name="Driver IC", category_type="raw_material"))
            db.add(Category(name="Connector", category_type="raw_material"))
            db.add(Category(name="Cable/Wire", category_type="raw_material"))
            db.add(Category(name="Rental LED Panel", category_type="rental"))
            db.add(Category(name="Rental Controller", category_type="rental"))
            db.add(Category(name="Stage Equipment", category_type="rental"))

        if db.query(Item).count() == 0:
            db.add(Item(sku="LED-DISP-P3", name="P3 Indoor LED Display", description="3mm pitch indoor LED display panel", item_type="product", category_id=1, brand="Bigstar", model="BS-P3-IN", unit="panel", min_stock=10, unit_cost=150.0, selling_price=280.0))
            db.add(Item(sku="LED-MOD-RGB", name="RGB LED Module 256x128", description="Full color LED module", item_type="product", category_id=2, brand="Bigstar", model="BS-MOD-RGB", unit="module", min_stock=50, unit_cost=45.0, selling_price=85.0))
            db.add(Item(sku="CTRL-NOVASTAR", name="NovaStar MCTRL660", description="LED display controller", item_type="product", category_id=3, brand="NovaStar", model="MCTRL660", unit="pcs", min_stock=5, unit_cost=320.0, selling_price=550.0))
            db.add(Item(sku="PSU-5V60A", name="5V 60A Power Supply", description="Switching power supply for LED", item_type="product", category_id=4, brand="MeanWell", model="LRS-350-5", unit="pcs", min_stock=20, unit_cost=35.0, selling_price=60.0))
            db.add(Item(sku="CHIP-3528", name="SMD 3528 LED Chip", description="Red LED chip 3528 SMD", item_type="raw_material", category_id=6, brand="Epistar", model="3528-R", unit="reel", min_stock=100, unit_cost=0.05, selling_price=0.1))
            db.add(Item(sku="PCB-2L-FR4", name="2-Layer FR4 PCB", description="Double layer FR4 PCB for LED module", item_type="raw_material", category_id=7, brand="Generic", model="PCB-2L-FR4", unit="pcs", min_stock=200, unit_cost=2.5, selling_price=5.0))
            db.add(Item(sku="DRV-ICN2038", name="ICN2038 LED Driver", description="Constant current LED driver IC", item_type="raw_material", category_id=8, brand="iC-Nova", model="ICN2038", unit="reel", min_stock=500, unit_cost=1.2, selling_price=2.5))
            db.add(Item(sku="RNT-PANEL-P4", name="P4 Rental LED Panel", description="4.81mm pitch rental LED panel 500x500mm", item_type="rental", category_id=11, brand="Bigstar", model="BS-RP4-500", unit="panel", min_stock=200, unit_cost=180.0, selling_price=0.0, track_serial=True))
            db.add(Item(sku="RNT-CTRL-VX4S", name="NovaStar VX4S Controller", description="4K rental LED controller", item_type="rental", category_id=12, brand="NovaStar", model="VX4S", unit="pcs", min_stock=10, unit_cost=800.0, selling_price=0.0, track_serial=True))

            db.flush()
            items = db.query(Item).all()
            loc_main = db.query(Location).filter(Location.name == "Main Warehouse").first()
            loc_repair = db.query(Location).filter(Location.name == "Repair Center").first()
            loc_th = db.query(Location).filter(Location.name == "Thailand Office").first()
            if loc_main and loc_repair and loc_th:
                for item in items:
                    if item.item_type == "product":
                        db.add(Stock(item_id=item.id, location_id=loc_main.id, quantity=50))
                        db.add(Stock(item_id=item.id, location_id=loc_th.id, quantity=20))
                    elif item.item_type == "raw_material":
                        db.add(Stock(item_id=item.id, location_id=loc_main.id, quantity=500))
                    elif item.item_type == "rental":
                        db.add(Stock(item_id=item.id, location_id=loc_main.id, quantity=100))
                        db.add(Stock(item_id=item.id, location_id=loc_repair.id, quantity=10))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed error (may already exist): {e}")
    finally:
        db.close()

seed_data()

# Pydantic Schemas

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    role: str
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LocationCreate(BaseModel):
    name: str
    location_type: str = "warehouse"
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None

class LocationResponse(BaseModel):
    id: int
    name: str
    location_type: str
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool
    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    category_type: str = "product"
    parent_id: Optional[int] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    category_type: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True

class ItemCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    item_type: str = "product"
    category_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    unit: str = "pcs"
    min_stock: int = 0
    unit_cost: float = 0.0
    selling_price: float = 0.0
    track_serial: bool = False
    track_batch: bool = False

class ItemResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    item_type: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    unit: str
    min_stock: int
    unit_cost: float
    selling_price: float
    track_serial: bool
    track_batch: bool
    is_active: bool
    total_stock: int = 0
    class Config:
        from_attributes = True

class StockEntry(BaseModel):
    item_id: int
    quantity: int
    location_id: int
    serial_number: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None

class StockOutEntry(BaseModel):
    item_id: int
    quantity: int
    location_id: int
    serial_number: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    remarks: Optional[str] = None

class TransferEntry(BaseModel):
    item_id: int
    quantity: int
    from_location_id: int
    to_location_id: int
    serial_number: Optional[str] = None
    remarks: Optional[str] = None

class MovementResponse(BaseModel):
    id: int
    movement_type: str
    item_id: int
    item_name: str
    item_sku: str
    quantity: int
    serial_number: Optional[str] = None
    batch_number: Optional[str] = None
    from_location_name: Optional[str] = None
    to_location_name: Optional[str] = None
    reference_type: Optional[str] = None
    status: str
    performed_by_name: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class POCreate(BaseModel):
    po_number: str
    supplier_name: str
    supplier_contact: Optional[str] = None
    total_amount: float = 0.0
    expected_date: Optional[str] = None
    remarks: Optional[str] = None
    items: List[dict]

class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_name: str
    supplier_contact: Optional[str] = None
    total_amount: float
    status: str
    created_by_name: Optional[str] = None
    created_at: datetime.datetime
    expected_date: Optional[str] = None
    remarks: Optional[str] = None
    class Config:
        from_attributes = True

class DOCreate(BaseModel):
    do_number: str
    client_name: str
    client_address: Optional[str] = None
    client_contact: Optional[str] = None
    project_id: Optional[int] = None
    delivery_date: Optional[str] = None
    remarks: Optional[str] = None
    items: List[dict]

class DeliveryOrderResponse(BaseModel):
    id: int
    do_number: str
    client_name: str
    client_address: Optional[str] = None
    client_contact: Optional[str] = None
    project_id: Optional[int] = None
    status: str
    delivery_date: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime.datetime
    remarks: Optional[str] = None
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    project_manager_id: Optional[int] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    project_manager_name: Optional[str] = None
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class RepairTicketCreate(BaseModel):
    ticket_number: str
    item_id: int
    serial_number: Optional[str] = None
    client_name: Optional[str] = None
    issue_description: str
    location_id: Optional[int] = None
    remarks: Optional[str] = None

class RepairTicketResponse(BaseModel):
    id: int
    ticket_number: str
    item_id: int
    item_name: str
    serial_number: Optional[str] = None
    client_name: Optional[str] = None
    issue_description: str
    status: str
    technician_name: Optional[str] = None
    location_name: Optional[str] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    remarks: Optional[str] = None
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_items: int
    total_stock_value: float
    low_stock_count: int
    pending_movements: int
    pending_po: int
    pending_do: int
    active_projects: int
    open_repairs: int
    recent_movements: List[dict]

# Security
security_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), SECRET_KEY.encode(), 100000).hex()

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.datetime.utcnow(),
        "jti": secrets.token_hex(16)
    }
    import base64
    header_b64 = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode().rstrip("=")
    sig = hashlib.sha256(f"{header_b64}.{payload_b64}.{SECRET_KEY}".encode()).hexdigest()
    return f"{header_b64}.{payload_b64}.{sig}"

def verify_token(token: str) -> Optional[int]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_json = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)).decode()
        payload = json.loads(payload_json)
        sig_check = hashlib.sha256(f"{parts[0]}.{parts[1]}.{SECRET_KEY}".encode()).hexdigest()
        if sig_check != parts[2]:
            return None
        exp = datetime.datetime.fromisoformat(str(payload["exp"]).replace("Z", "+00:00").replace("+00:00", ""))
        if datetime.datetime.utcnow() > exp:
            return None
        return int(payload["sub"])
    except Exception:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def require_role(*roles: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail=f"Required role: {', '.join(roles)}")
        return user
    return checker

# FastAPI App

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="BIMS API", version="2.0.0", lifespan=lifespan)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

# Auth Endpoints

@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == req.username).first()
    db.close()
    if not user or hash_password(req.password) != user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user

# Dashboard

@app.get("/api/dashboard", response_model=DashboardStats)
def dashboard(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        total_items = db.query(Item).filter(Item.is_active == True).count()
        low_stock = 0
        stock_items = db.query(Stock).all()
        total_val = 0.0
        for s in stock_items:
            item = db.query(Item).filter(Item.id == s.item_id).first()
            if item:
                total_val += s.quantity * item.unit_cost
                if s.quantity <= item.min_stock:
                    low_stock += 1

        pending_mv = db.query(StockMovement).filter(StockMovement.status == "pending").count()
        pending_po = db.query(PurchaseOrder).filter(PurchaseOrder.status.in_(["draft", "sent", "partial"])).count()
        pending_do = db.query(DeliveryOrder).filter(DeliveryOrder.status.in_(["draft", "picking", "ready", "shipped"])).count()
        active_prj = db.query(Project).filter(Project.status == "active").count()
        open_rep = db.query(RepairTicket).filter(RepairTicket.status.notin_(["completed", "returned"])).count()

        recent = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(10).all()
        recent_list = []
        for mv in recent:
            item = db.query(Item).filter(Item.id == mv.item_id).first()
            perf = db.query(User).filter(User.id == mv.performed_by).first()
            recent_list.append({
                "id": mv.id, "movement_type": mv.movement_type,
                "item_name": item.name if item else "Unknown",
                "quantity": mv.quantity, "status": mv.status,
                "performed_by": perf.full_name if perf else "Unknown",
                "created_at": str(mv.created_at)
            })

        return DashboardStats(
            total_items=total_items, total_stock_value=round(total_val, 2),
            low_stock_count=low_stock, pending_movements=pending_mv,
            pending_po=pending_po, pending_do=pending_do,
            active_projects=active_prj, open_repairs=open_rep,
            recent_movements=recent_list
        )
    finally:
        db.close()

# Items

@app.get("/api/items")
def list_items(
    search: Optional[str] = None, item_type: Optional[str] = None,
    category_id: Optional[int] = None, location_id: Optional[int] = None,
    low_stock_only: bool = False, page: int = 1, limit: int = 50,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(Item).filter(Item.is_active == True)
        if search:
            q = q.filter(Item.name.contains(search) | Item.sku.contains(search) | Item.brand.contains(search))
        if item_type:
            q = q.filter(Item.item_type == item_type)
        if category_id:
            q = q.filter(Item.category_id == category_id)
        total = q.count()
        items = q.offset((page - 1) * limit).limit(limit).all()

        result = []
        for item in items:
            cat = db.query(Category).filter(Category.id == item.category_id).first()
            stocks = db.query(Stock).filter(Stock.item_id == item.id)
            if location_id:
                stocks = stocks.filter(Stock.location_id == location_id)
            total_stock = sum(s.quantity for s in stocks.all())
            is_low = total_stock <= item.min_stock
            if low_stock_only and not is_low:
                continue

            result.append({
                "id": item.id, "sku": item.sku, "name": item.name,
                "description": item.description, "item_type": item.item_type,
                "category_id": item.category_id, "category_name": cat.name if cat else None,
                "brand": item.brand, "model": item.model, "unit": item.unit,
                "min_stock": item.min_stock, "unit_cost": item.unit_cost,
                "selling_price": item.selling_price, "track_serial": item.track_serial,
                "track_batch": item.track_batch, "is_active": item.is_active,
                "total_stock": total_stock, "is_low_stock": is_low,
                "created_at": str(item.created_at)
            })
        return {"items": result, "total": total, "page": page, "pages": (total + limit - 1) // limit}
    finally:
        db.close()

@app.post("/api/items", status_code=201)
def create_item(item: ItemCreate, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        db_item = Item(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return {"id": db_item.id, "sku": db_item.sku, "name": db_item.name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/api/items/{item_id}")
def get_item(item_id: int, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        cat = db.query(Category).filter(Category.id == item.category_id).first()
        stocks = db.query(Stock).filter(Stock.item_id == item.id).all()
        stock_details = []
        for s in stocks:
            loc = db.query(Location).filter(Location.id == s.location_id).first()
            stock_details.append({"location_id": s.location_id, "location_name": loc.name if loc else "Unknown", "quantity": s.quantity, "serial_number": s.serial_number, "batch_number": s.batch_number, "status": s.status})
        return {
            "id": item.id, "sku": item.sku, "name": item.name, "description": item.description,
            "item_type": item.item_type, "category_id": item.category_id, "category_name": cat.name if cat else None,
            "brand": item.brand, "model": item.model, "unit": item.unit, "min_stock": item.min_stock,
            "unit_cost": item.unit_cost, "selling_price": item.selling_price, "track_serial": item.track_serial,
            "track_batch": item.track_batch, "is_active": item.is_active, "stock": stock_details
        }
    finally:
        db.close()

@app.put("/api/items/{item_id}")
def update_item(item_id: int, item: ItemCreate, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        for k, v in item.model_dump().items():
            setattr(db_item, k, v)
        db.commit()
        return {"message": "Item updated"}
    finally:
        db.close()

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, user: User = Depends(require_role("management"))):
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        db_item.is_active = False
        db.commit()
        return {"message": "Item deactivated"}
    finally:
        db.close()

# Stock In

@app.post("/api/stock/in")
def stock_in(data: StockEntry, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        loc = db.query(Location).filter(Location.id == data.location_id).first()
        if not loc:
            raise HTTPException(status_code=404, detail="Location not found")

        existing = db.query(Stock).filter(
            Stock.item_id == data.item_id,
            Stock.location_id == data.location_id,
            Stock.serial_number == data.serial_number,
            Stock.batch_number == data.batch_number
        ).first()
        if existing:
            existing.quantity += data.quantity
        else:
            db.add(Stock(item_id=data.item_id, location_id=data.location_id, quantity=data.quantity,
                        serial_number=data.serial_number, batch_number=data.batch_number,
                        expiry_date=datetime.datetime.strptime(data.expiry_date, "%Y-%m-%d").date() if data.expiry_date else None))

        mv = StockMovement(movement_type="in", item_id=data.item_id, serial_number=data.serial_number,
                          batch_number=data.batch_number, quantity=data.quantity,
                          to_location_id=data.location_id, performed_by=user.id, status="approved", approved_by=user.id)
        db.add(mv)
        db.commit()
        return {"message": f"Stocked in {data.quantity} {item.unit} of {item.name} at {loc.name}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Stock Out

@app.post("/api/stock/out")
def stock_out(data: StockOutEntry, user: User = Depends(require_role("management", "warehouse", "sales", "pm"))):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        loc = db.query(Location).filter(Location.id == data.location_id).first()
        if not loc:
            raise HTTPException(status_code=404, detail="Location not found")

        stock = db.query(Stock).filter(
            Stock.item_id == data.item_id,
            Stock.location_id == data.location_id,
            Stock.serial_number == data.serial_number
        ).first()
        if not stock or stock.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        stock.quantity -= data.quantity
        if stock.quantity == 0:
            db.delete(stock)

        mv = StockMovement(movement_type="out", item_id=data.item_id, serial_number=data.serial_number,
                          quantity=data.quantity, from_location_id=data.location_id,
                          reference_type=data.reference_type, reference_id=data.reference_id,
                          performed_by=user.id, status="approved" if user.role in ["management", "warehouse"] else "pending",
                          remarks=data.remarks)
        db.add(mv)
        db.commit()
        return {"message": f"Stocked out {data.quantity} {item.unit} of {item.name} from {loc.name}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Stock Transfer

@app.post("/api/stock/transfer")
def stock_transfer(data: TransferEntry, user: User = Depends(require_role("management", "warehouse", "pm"))):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        from_loc = db.query(Location).filter(Location.id == data.from_location_id).first()
        to_loc = db.query(Location).filter(Location.id == data.to_location_id).first()
        if not from_loc or not to_loc:
            raise HTTPException(status_code=404, detail="Location not found")

        stock = db.query(Stock).filter(
            Stock.item_id == data.item_id, Stock.location_id == data.from_location_id,
            Stock.serial_number == data.serial_number
        ).first()
        if not stock or stock.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock at source location")

        stock.quantity -= data.quantity
        if stock.quantity == 0:
            db.delete(stock)

        existing_dest = db.query(Stock).filter(
            Stock.item_id == data.item_id, Stock.location_id == data.to_location_id,
            Stock.serial_number == data.serial_number
        ).first()
        if existing_dest:
            existing_dest.quantity += data.quantity
        else:
            db.add(Stock(item_id=data.item_id, location_id=data.to_location_id, quantity=data.quantity,
                        serial_number=data.serial_number))

        mv = StockMovement(movement_type="transfer", item_id=data.item_id, serial_number=data.serial_number,
                          quantity=data.quantity, from_location_id=data.from_location_id,
                          to_location_id=data.to_location_id, performed_by=user.id,
                          status="approved" if user.role == "management" else "pending", remarks=data.remarks)
        db.add(mv)
        db.commit()
        return {"message": f"Transferred {data.quantity} {item.unit} of {item.name} from {from_loc.name} to {to_loc.name}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Stock Movements

@app.get("/api/stock/movements")
def list_movements(
    movement_type: Optional[str] = None, status: Optional[str] = None,
    page: int = 1, limit: int = 50,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(StockMovement).order_by(StockMovement.created_at.desc())
        if movement_type:
            q = q.filter(StockMovement.movement_type == movement_type)
        if status:
            q = q.filter(StockMovement.status == status)
        total = q.count()
        movements = q.offset((page - 1) * limit).limit(limit).all()
        result = []
        for mv in movements:
            item = db.query(Item).filter(Item.id == mv.item_id).first()
            perf = db.query(User).filter(User.id == mv.performed_by).first()
            from_loc = db.query(Location).filter(Location.id == mv.from_location_id).first() if mv.from_location_id else None
            to_loc = db.query(Location).filter(Location.id == mv.to_location_id).first() if mv.to_location_id else None
            result.append({
                "id": mv.id, "movement_type": mv.movement_type,
                "item_id": mv.item_id, "item_name": item.name if item else "Unknown",
                "item_sku": item.sku if item else "", "quantity": mv.quantity,
                "serial_number": mv.serial_number, "batch_number": mv.batch_number,
                "from_location_name": from_loc.name if from_loc else None,
                "to_location_name": to_loc.name if to_loc else None,
                "reference_type": mv.reference_type, "status": mv.status,
                "performed_by_name": perf.full_name if perf else "Unknown",
                "remarks": mv.remarks, "created_at": str(mv.created_at)
            })
        return {"movements": result, "total": total, "page": page}
    finally:
        db.close()

@app.post("/api/stock/movements/{mv_id}/approve")
def approve_movement(mv_id: int, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        mv = db.query(StockMovement).filter(StockMovement.id == mv_id).first()
        if not mv:
            raise HTTPException(status_code=404, detail="Movement not found")
        mv.status = "approved"
        mv.approved_by = user.id
        db.commit()
        return {"message": "Movement approved"}
    finally:
        db.close()

@app.post("/api/stock/movements/{mv_id}/reject")
def reject_movement(mv_id: int, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        mv = db.query(StockMovement).filter(StockMovement.id == mv_id).first()
        if not mv:
            raise HTTPException(status_code=404, detail="Movement not found")
        mv.status = "rejected"
        mv.approved_by = user.id
        db.commit()
        return {"message": "Movement rejected"}
    finally:
        db.close()

# Locations

@app.get("/api/locations")
def list_locations(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        locs = db.query(Location).filter(Location.is_active == True).all()
        return {"locations": [{"id": l.id, "name": l.name, "location_type": l.location_type, "address": l.address, "contact_person": l.contact_person, "contact_phone": l.contact_phone, "is_active": l.is_active} for l in locs]}
    finally:
        db.close()

@app.post("/api/locations", status_code=201)
def create_location(loc: LocationCreate, user: User = Depends(require_role("management"))):
    db = SessionLocal()
    try:
        db_loc = Location(**loc.model_dump())
        db.add(db_loc)
        db.commit()
        db.refresh(db_loc)
        return {"id": db_loc.id, "name": db_loc.name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Categories

@app.get("/api/categories")
def list_categories(category_type: Optional[str] = None, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(Category)
        if category_type:
            q = q.filter(Category.category_type == category_type)
        cats = q.all()
        return {"categories": [{"id": c.id, "name": c.name, "category_type": c.category_type, "parent_id": c.parent_id, "description": c.description} for c in cats]}
    finally:
        db.close()

@app.post("/api/categories", status_code=201)
def create_category(cat: CategoryCreate, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        db_cat = Category(**cat.model_dump())
        db.add(db_cat)
        db.commit()
        db.refresh(db_cat)
        return {"id": db_cat.id, "name": db_cat.name}
    finally:
        db.close()

# Purchase Orders

@app.get("/api/purchase-orders")
def list_pos(status: Optional[str] = None, page: int = 1, limit: int = 50, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc())
        if status:
            q = q.filter(PurchaseOrder.status == status)
        total = q.count()
        pos = q.offset((page - 1) * limit).limit(limit).all()
        result = []
        for po in pos:
            creator = db.query(User).filter(User.id == po.created_by).first()
            items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.po_id == po.id).all()
            result.append({
                "id": po.id, "po_number": po.po_number, "supplier_name": po.supplier_name,
                "supplier_contact": po.supplier_contact, "total_amount": po.total_amount,
                "status": po.status, "created_by_name": creator.full_name if creator else "Unknown",
                "created_at": str(po.created_at), "expected_date": str(po.expected_date) if po.expected_date else None,
                "remarks": po.remarks, "item_count": len(items)
            })
        return {"purchase_orders": result, "total": total, "page": page}
    finally:
        db.close()

@app.post("/api/purchase-orders", status_code=201)
def create_po(po: POCreate, user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        db_po = PurchaseOrder(po_number=po.po_number, supplier_name=po.supplier_name,
                             supplier_contact=po.supplier_contact, total_amount=po.total_amount,
                             created_by=user.id, expected_date=datetime.datetime.strptime(po.expected_date, "%Y-%m-%d").date() if po.expected_date else None,
                             remarks=po.remarks)
        db.add(db_po)
        db.commit()
        db.refresh(db_po)
        for it in po.items:
            db.add(PurchaseOrderItem(po_id=db_po.id, item_id=it.get("item_id"), quantity=it.get("quantity", 0), unit_price=it.get("unit_price", 0.0)))
        db.commit()
        return {"id": db_po.id, "po_number": db_po.po_number}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/api/purchase-orders/{po_id}")
def get_po(po_id: int, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise HTTPException(status_code=404, detail="PO not found")
        creator = db.query(User).filter(User.id == po.created_by).first()
        items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.po_id == po.id).all()
        item_list = []
        for it in items:
            item = db.query(Item).filter(Item.id == it.item_id).first()
            item_list.append({"id": it.id, "item_id": it.item_id, "item_name": item.name if item else "Unknown",
                             "item_sku": item.sku if item else "", "quantity": it.quantity,
                             "unit_price": it.unit_price, "received_qty": it.received_qty})
        return {
            "id": po.id, "po_number": po.po_number, "supplier_name": po.supplier_name,
            "supplier_contact": po.supplier_contact, "total_amount": po.total_amount,
            "status": po.status, "created_by_name": creator.full_name if creator else "Unknown",
            "created_at": str(po.created_at), "expected_date": str(po.expected_date) if po.expected_date else None,
            "remarks": po.remarks, "items": item_list
        }
    finally:
        db.close()

@app.put("/api/purchase-orders/{po_id}/status")
def update_po_status(po_id: int, status: str = Body(..., embed=True), user: User = Depends(require_role("management", "warehouse"))):
    db = SessionLocal()
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise HTTPException(status_code=404, detail="PO not found")
        po.status = status
        db.commit()
        return {"message": "Status updated"}
    finally:
        db.close()

# Delivery Orders

@app.get("/api/delivery-orders")
def list_dos(status: Optional[str] = None, page: int = 1, limit: int = 50, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(DeliveryOrder).order_by(DeliveryOrder.created_at.desc())
        if status:
            q = q.filter(DeliveryOrder.status == status)
        total = q.count()
        dos = q.offset((page - 1) * limit).limit(limit).all()
        result = []
        for do in dos:
            creator = db.query(User).filter(User.id == do.created_by).first()
            result.append({
                "id": do.id, "do_number": do.do_number, "client_name": do.client_name,
                "client_address": do.client_address, "client_contact": do.client_contact,
                "project_id": do.project_id, "status": do.status,
                "delivery_date": str(do.delivery_date) if do.delivery_date else None,
                "created_by_name": creator.full_name if creator else "Unknown",
                "created_at": str(do.created_at), "remarks": do.remarks
            })
        return {"delivery_orders": result, "total": total, "page": page}
    finally:
        db.close()

@app.post("/api/delivery-orders", status_code=201)
def create_do(do: DOCreate, user: User = Depends(require_role("management", "sales", "warehouse"))):
    db = SessionLocal()
    try:
        db_do = DeliveryOrder(do_number=do.do_number, client_name=do.client_name,
                             client_address=do.client_address, client_contact=do.client_contact,
                             project_id=do.project_id, created_by=user.id,
                             delivery_date=datetime.datetime.strptime(do.delivery_date, "%Y-%m-%d").date() if do.delivery_date else None,
                             remarks=do.remarks)
        db.add(db_do)
        db.commit()
        db.refresh(db_do)
        for it in do.items:
            db.add(DeliveryOrderItem(do_id=db_do.id, item_id=it.get("item_id"), quantity=it.get("quantity", 0), serial_number=it.get("serial_number")))
        db.commit()
        return {"id": db_do.id, "do_number": db_do.do_number}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/api/delivery-orders/{do_id}")
def get_do(do_id: int, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        do = db.query(DeliveryOrder).filter(DeliveryOrder.id == do_id).first()
        if not do:
            raise HTTPException(status_code=404, detail="DO not found")
        creator = db.query(User).filter(User.id == do.created_by).first()
        items = db.query(DeliveryOrderItem).filter(DeliveryOrderItem.do_id == do.id).all()
        item_list = []
        for it in items:
            item = db.query(Item).filter(Item.id == it.item_id).first()
            item_list.append({"id": it.id, "item_id": it.item_id, "item_name": item.name if item else "Unknown",
                             "item_sku": item.sku if item else "", "quantity": it.quantity, "serial_number": it.serial_number})
        return {
            "id": do.id, "do_number": do.do_number, "client_name": do.client_name,
            "client_address": do.client_address, "client_contact": do.client_contact,
            "project_id": do.project_id, "status": do.status,
            "delivery_date": str(do.delivery_date) if do.delivery_date else None,
            "created_by_name": creator.full_name if creator else "Unknown",
            "created_at": str(do.created_at), "remarks": do.remarks, "items": item_list
        }
    finally:
        db.close()

@app.put("/api/delivery-orders/{do_id}/status")
def update_do_status(do_id: int, status: str = Body(..., embed=True), user: User = Depends(require_role("management", "warehouse", "sales"))):
    db = SessionLocal()
    try:
        do = db.query(DeliveryOrder).filter(DeliveryOrder.id == do_id).first()
        if not do:
            raise HTTPException(status_code=404, detail="DO not found")
        do.status = status
        db.commit()
        return {"message": "Status updated"}
    finally:
        db.close()

# Projects

@app.get("/api/projects")
def list_projects(status: Optional[str] = None, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(Project).order_by(Project.created_at.desc())
        if status:
            q = q.filter(Project.status == status)
        projects = q.all()
        result = []
        for p in projects:
            pm = db.query(User).filter(User.id == p.project_manager_id).first()
            result.append({
                "id": p.id, "name": p.name, "description": p.description,
                "client_name": p.client_name, "status": p.status,
                "start_date": str(p.start_date) if p.start_date else None,
                "end_date": str(p.end_date) if p.end_date else None,
                "project_manager_name": pm.full_name if pm else None,
                "created_at": str(p.created_at)
            })
        return {"projects": result}
    finally:
        db.close()

@app.post("/api/projects", status_code=201)
def create_project(project: ProjectCreate, user: User = Depends(require_role("management", "pm"))):
    db = SessionLocal()
    try:
        db_p = Project(**{k: v for k, v in project.model_dump().items() if v is not None})
        if project.start_date:
            db_p.start_date = datetime.datetime.strptime(project.start_date, "%Y-%m-%d").date()
        if project.end_date:
            db_p.end_date = datetime.datetime.strptime(project.end_date, "%Y-%m-%d").date()
        db.add(db_p)
        db.commit()
        db.refresh(db_p)
        return {"id": db_p.id, "name": db_p.name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.put("/api/projects/{project_id}")
def update_project(project_id: int, project: ProjectCreate, user: User = Depends(require_role("management", "pm"))):
    db = SessionLocal()
    try:
        db_p = db.query(Project).filter(Project.id == project_id).first()
        if not db_p:
            raise HTTPException(status_code=404, detail="Project not found")
        for k, v in project.model_dump().items():
            if v is not None:
                if k in ("start_date", "end_date"):
                    v = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                setattr(db_p, k, v)
        db.commit()
        return {"message": "Project updated"}
    finally:
        db.close()

# Repair Tickets

@app.get("/api/repair-tickets")
def list_repairs(status: Optional[str] = None, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(RepairTicket).order_by(RepairTicket.created_at.desc())
        if status:
            q = q.filter(RepairTicket.status == status)
        tickets = q.all()
        result = []
        for t in tickets:
            item = db.query(Item).filter(Item.id == t.item_id).first()
            tech = db.query(User).filter(User.id == t.technician_id).first()
            loc = db.query(Location).filter(Location.id == t.location_id).first()
            result.append({
                "id": t.id, "ticket_number": t.ticket_number,
                "item_id": t.item_id, "item_name": item.name if item else "Unknown",
                "serial_number": t.serial_number, "client_name": t.client_name,
                "issue_description": t.issue_description, "status": t.status,
                "technician_name": tech.full_name if tech else None,
                "location_name": loc.name if loc else None,
                "created_at": str(t.created_at),
                "completed_at": str(t.completed_at) if t.completed_at else None,
                "remarks": t.remarks
            })
        return {"repair_tickets": result}
    finally:
        db.close()

@app.post("/api/repair-tickets", status_code=201)
def create_repair(ticket: RepairTicketCreate, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        db_t = RepairTicket(ticket_number=ticket.ticket_number, item_id=ticket.item_id,
                           serial_number=ticket.serial_number, client_name=ticket.client_name,
                           issue_description=ticket.issue_description, location_id=ticket.location_id,
                           created_by=user.id, remarks=ticket.remarks)
        db.add(db_t)
        db.commit()
        db.refresh(db_t)
        return {"id": db_t.id, "ticket_number": db_t.ticket_number}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.put("/api/repair-tickets/{ticket_id}/status")
def update_repair_status(ticket_id: int, status: str = Body(..., embed=True), technician_id: Optional[int] = Body(None, embed=True), user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        t = db.query(RepairTicket).filter(RepairTicket.id == ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        t.status = status
        if technician_id:
            t.technician_id = technician_id
        if status in ("completed", "returned"):
            t.completed_at = datetime.datetime.utcnow()
        db.commit()
        return {"message": "Status updated"}
    finally:
        db.close()

# Users

@app.get("/api/users")
def list_users(user: User = Depends(require_role("management"))):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return {"users": [{"id": u.id, "username": u.username, "full_name": u.full_name, "email": u.email, "role": u.role, "is_active": u.is_active} for u in users]}
    finally:
        db.close()

@app.post("/api/users", status_code=201)
def create_user(data: dict = Body(...), user: User = Depends(require_role("management"))):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == data["username"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        new_user = User(
            username=data["username"], full_name=data.get("full_name", data["username"]),
            email=data.get("email"), password_hash=hash_password(data["password"]),
            role=data.get("role", "warehouse")
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "username": new_user.username}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Frontend SPA Fallback

@app.get("/")
def serve_index():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)

@app.get("/{path:path}")
def serve_spa(path: str):
    if path.startswith("api/") or path.startswith("assets/"):
        raise HTTPException(status_code=404, detail="Not found")
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
