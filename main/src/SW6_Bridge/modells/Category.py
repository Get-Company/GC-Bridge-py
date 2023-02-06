from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from main.src.SW6_Bridge.modells import db


class Category(db.Base):
    __tablename__ = "bridge_category_entity"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    erp_nr = Column(Integer, nullable=False)
    api_id = Column(String(32), nullable=False)
    erp_nr_parent = Column(Integer, nullable=True)
    api_idparent = Column(String(32), nullable=True)
    title = Column(String(50), nullable=True)
    image = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    erp_ltz_aend = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now())

    # products = relationship(
    #     'BridgeProductEntity',
    #     secondary=product_category,
    #     back_populates='categories',
    #     lazy='dynamic')

    product_category_relation = relationship("ProductCategoryRelation", back_populates="category")

    def __repr__(self):
        return f"Category(id={self.id!r}, title={self.title!r})"

    def insert(self, category_rows):
        self.logger.info(f"Try to insert data into {self.__tablename__} table")
        results = db.session.add_all(category_rows)
        self.logger.info(f"Inserting into {self.__tablename__} table has been finished. {results.rowcount}")

    def update(self, new_category):
        self.logger.info(f"Try to update {self.__tablename__} table")
        self.erp_nr = new_category.erp_nr
        self.api_id = new_category.api_id
        self.erp_nr_parent = new_category.erp_nr_parent
        self.api_idparent = new_category.api_idparent
        self.title = new_category.title
        self.image = new_category.image
        self.description = new_category.description
        self.erp_ltz_aend = new_category.erp_ltz_aend
        self.created_at = new_category.created_at
        db.session.commit()
        self.logger.info(f"Updating {self.__tablename__} table finished.")