from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SerialNumber(Base):
    __tablename__ = "serial_numbers"

    id = Column(Integer, primary_key=True, index=True)
    serial_code = Column(String, unique=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    status = Column(String, default="in_stock")
    location_id = Column(Integer, ForeignKey("locations.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="serial_numbers")
