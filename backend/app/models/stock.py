from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    quantity = Column(Integer, default=0)
    reserved_qty = Column(Integer, default=0)
    unit_cost = Column(Numeric(12, 2), default=0)

    item = relationship("Item", back_populates="stocks")
    location = relationship("Location", back_populates="stocks")
    project = relationship("Project", back_populates="stocks")
