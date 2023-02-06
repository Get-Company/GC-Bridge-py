from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from main.src.SW6_Bridge.config.config import config



class db:
    engine = create_engine(config['sqlalchemy_url'], future=True)
    Base = declarative_base()
    Metadata = Base.metadata
    session = Session(engine)


from main.src.SW6_Bridge.modells.Category import Category
from main.src.SW6_Bridge.modells.Pruduct import Product
from main.src.SW6_Bridge.modells.Customer import CustomerAddress, Customer
from main.src.SW6_Bridge.modells.Relations import *
from main.src.SW6_Bridge.modells.Tax import *
from main.src.SW6_Bridge.modells.Orders import *
from main.src.SW6_Bridge.modells.Sync import *



__all__ = ["db", "Category", "Product", "ProductCategoryRelation", "CustomerAddress", "Customer", "Tax", "Synchronize"]

