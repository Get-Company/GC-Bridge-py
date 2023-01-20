from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer_address'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relationship("Address", back_populates="customer_address")

    default_address_id = Column(Integer, ForeignKey('address.id'))
    default_address = relationship("Address", uselist=False)


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    street = Column(String)
    city = Column(String)
    zip = Column(String)

    customer_id = Column(Integer, ForeignKey('customer_address.id'))
    customer = relationship("Customer", back_populates="addresses")
