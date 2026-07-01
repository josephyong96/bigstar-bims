from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    unit = Column(String, default="pcs")
    reorder_level = Column(Integer, default=0)
    status = Column(String, default="active")
    
    category = relationship("Category", back_populates="items")
    stocks = relationship("Stock", back_populates="item")
    serial_numbers = relationship("SerialNumber", back_populates="item")
    batch_numbers = relationship("BatchNumber", back_populates="item")
