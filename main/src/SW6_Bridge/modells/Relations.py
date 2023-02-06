from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from main.src.SW6_Bridge.modells import db

class ProductCategoryRelation(db.Base):
    __tablename__ = "bridge_product_category_entity"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("bridge_product_entity.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("bridge_category_entity.id"), nullable=False)

    product = relationship("Product", back_populates="product_category_relation")
    category = relationship("Category", back_populates="product_category_relation")

