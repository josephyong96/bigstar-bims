from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BatchNumber(Base):
    __tablename__ = "batch_numbers"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String, unique=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    supplier_batch = Column(String)
    manufacture_date = Column(DateTime)
    expiry_date = Column(DateTime)
    quantity = Column(Integer, default=0)
    status = Column(String, default="active")
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    item = relationship("Item", back_populates="batch_numbers")
