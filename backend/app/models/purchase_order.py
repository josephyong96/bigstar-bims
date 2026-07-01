from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, nullable=False)
    supplier_name = Column(String, nullable=False)
    order_date = Column(DateTime, nullable=False)
    expected_date = Column(DateTime)
    total_amount = Column(Numeric(12, 2), default=0)
    status = Column(String, default="pending")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    po_items = relationship("POItem", back_populates="purchase_order")
