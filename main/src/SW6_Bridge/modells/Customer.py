from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, CHAR, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from main.src.SW6_Bridge.modells import db


class CustomerAddress(db.Base):
    __tablename__ = 'bridge_customer_address_entity'
    __table_args__ = (UniqueConstraint('erp_nr', 'erp_ansnr', 'erp_aspnr', name='unique_erp_nr_ansnr_aspnr'),)

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = Column(CHAR(36), nullable=False)
    erp_nr = Column(CHAR(10), nullable=True)
    erp_ansnr = Column(Integer(), nullable=True)
    erp_aspnr = Column(Integer(), nullable=True)
    na1 = Column(String(255), nullable=False)
    na2 = Column(String(255), nullable=False)
    na3 = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    str = Column(String(255), nullable=True)
    plz = Column(CHAR(12), nullable=True)
    city = Column(String(255), nullable=True)
    land = Column(Integer(), nullable=True)
    land_ISO2 = Column(String(2), nullable=True)
    company = Column(String(255), nullable=True)
    erp_ltz_aend = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), default=datetime.now())  # Delete and refactor
    updated_at = Column(DateTime(), default=datetime.now())

    """
    Relations
    """

    # Customer aka DataSet Adressen many - to -one
    customer = relationship('Customer', back_populates='addresses')
    customer_id = Column(Integer(), ForeignKey('bridge_customer_entity.id'))

    #################

    def __repr__(self):
        return f"Address(id={self.id!r}, company={self.company!r})"



class Customer(db.Base):
    __tablename__ = 'bridge_customer_entity'

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = Column(CHAR(36), nullable=False)
    erp_nr = Column(CHAR(10), nullable=True)
    email = Column(String(255), nullable=True)
    ustid = Column(String(255), nullable=True)
    erp_reansnr = Column(Integer(), nullable=True)
    erp_liansnr = Column(Integer(), nullable=True)
    erp_ltz_aend = Column(DateTime(), nullable=True)  # Delete this and refactor
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now())

    """
    Relations
    """
    # Relation one - to -many
    addresses = relationship(
        'CustomerAddress',
        back_populates="customer")

    # Relation one - to -many
    orders = relationship(
        'Order',
        back_populates="customer")

    def __repr__(self):
        return f"Customer: {self.id} - {self.erp_nr}"