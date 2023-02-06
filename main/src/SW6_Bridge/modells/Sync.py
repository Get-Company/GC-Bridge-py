from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, CHAR, UniqueConstraint, BOOLEAN
from sqlalchemy.orm import relationship
from datetime import datetime
from main.src.SW6_Bridge.modells import db


class Synchronize(db.Base):
    __tablename__ = 'bridge_synchronize_entity'
    id = Column(Integer(), primary_key=True, nullable=False, unique=True)
    dataset_category_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    dataset_product_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    dataset_customers_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    dataset_tax_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    dataset_order_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    # SW6 Fields
    sw6_category_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    sw6_product_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    sw6_customers_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    sw6_order_sync_date = Column(DateTime(), nullable=True, default=datetime.now())
    # Loop True or false
    loop_continue = Column(BOOLEAN, nullable=True)

    def __repr__(self):
        return "Synchronize Created/Updated"

