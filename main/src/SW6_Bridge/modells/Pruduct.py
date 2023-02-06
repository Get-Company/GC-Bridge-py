from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from main.src.SW6_Bridge.modells import db


class Product(db.Base):
    __tablename__ = "bridge_product_entity"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    erp_nr = Column(String(12), nullable=False)
    api_id = Column(String(32), nullable=False)
    name = Column(String(50), nullable=False)
    image = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    price_rebate_amount = Column(Integer, nullable=True)
    price_rebate = Column(Float, nullable=True)
    stock = Column(Integer, nullable=True)
    factor = Column(String(50), nullable=True)
    min_purchase = Column(Integer, nullable=True)
    purchase_unit = Column(String(10), nullable=True)
    unit = Column(String(10), nullable=True)
    erp_ltz_aend = Column(String(50), nullable=True)
    wshopkz = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    #### RELATIONS #####
    product_category_relation = relationship("ProductCategoryRelation", back_populates="product")
    tax_id = Column(Integer, ForeignKey('bridge_tax_entity.id'))
    tax = relationship('Tax')


    def __repr__(self):
        return f"Product(id={self.id!r}, name={self.name!r})"

    def insert(self, product_rows):
        self.logger.info(f"Try to insert data into {self.__tablename__} table")
        results = db.session.add_all(product_rows)
        self.logger.info(f"Inserting into {self.__tablename__} table has been finished. {results.rowcount}")

    def update(self, new_product):
        self.logger.info(f"Try to update {self.__tablename__} table")
        self.erp_nr = new_product.erp_nr
        self.api_id = new_product.api_id
        self.name = new_product.name
        self.image = new_product.image
        self.description = new_product.description
        self.price = new_product.price
        self.price_rebate_amount = new_product.price_rebate_amount
        self.price_rebate = new_product.price_rebate
        self.stock = new_product.stock
        self.factor = new_product.factor
        self.min_purchase = new_product.min_purchase
        self.purchase_unit = new_product.purchase_unit
        self.unit = new_product.unit
        self.erp_ltz_aend = new_product.erp_ltz_aend
        self.wshopkz = new_product.wshopkz
        self.tax_id = new_product.tax_id
        self.created_at = new_product.created_at
        db.session.commit()
        self.logger.info(f"Updating {self.__tablename__} table finished.")