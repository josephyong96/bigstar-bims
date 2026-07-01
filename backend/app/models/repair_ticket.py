from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RepairTicket(Base):
    __tablename__ = "repair_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    serial_id = Column(Integer, ForeignKey("serial_numbers.id"))
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_description = Column(Text, nullable=False)
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    assigned_to = Column(Integer, ForeignKey("users.id"))
    resolution_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime)

    item = relationship("Item")
