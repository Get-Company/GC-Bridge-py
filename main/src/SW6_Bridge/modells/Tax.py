from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Text, CHAR
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from main.src.SW6_Bridge.modells import db

class Tax(db.Base):
    __tablename__ = 'bridge_tax_entity'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    steuer_schluessel = Column(Integer, nullable=True)
    description = Column(String(255), nullable=True)
    satz = Column(Float(), nullable=True)
    api_id = Column(CHAR(36), nullable=False)
    ### Relations ###
    products = relationship("Product", back_populates="tax")

    def __repr__(self):
        return f"Tax {self.description}({self.satz}%)"