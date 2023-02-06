from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Text, CHAR
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from main.src.SW6_Bridge.modells import db



class Order(db.Base):
    __tablename__ = "bridge_order_entity"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    api_id = Column(CHAR(36), nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now())
    edited_at = Column(DateTime, nullable=False)

    """
    Relations
    """
    # Relation many - to - one
    customer = relationship("Customer",  back_populates="orders")
    customer_id = Column(Integer(), ForeignKey('bridge_customer_entity.id'))