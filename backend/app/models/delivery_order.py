"""Delivery Order model for BIMS."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DeliveryOrder(Base):
    """Delivery Order / Stock Out document."""

    __tablename__ = "delivery_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    do_number = Column(String(50), unique=True, nullable=False)
    client_name = Column(String(200), nullable=False)
    project_name = Column(String(200), nullable=True)
    delivery_address = Column(Text, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    status = Column(
        Enum("pending", "approved", "picked", "packed", "shipped", "delivered", "cancelled", name="do_status"),
        default="pending", nullable=False,
    )
    notes = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    shipped_date = Column(DateTime, nullable=True)
    delivered_date = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<DeliveryOrder {self.do_number}>"
