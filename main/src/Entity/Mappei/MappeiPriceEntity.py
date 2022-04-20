from main import db
from datetime import datetime
import json


# Make themappei price class
class MappeiPriceEntity(db.Model):
    __tablename__ = 'mappei_price_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    price_high = db.Column(db.Float(), nullable=True)
    price_low = db.Column(db.Float(), nullable=True)
    price_quantity = db.Column(db.Integer(), nullable=True)
    land = db.Column(db.String(255), nullable=True)
    last_mod = db.Column(db.DateTime(), default=datetime.now())

    # Mappei Product many - to - one
    product_id = db.Column(db.Integer, db.ForeignKey('mappei_product_entity.id'))
    product = db.relationship('MappeiProductEntity', back_populates='prices')

    def __repr__(self):
        return f"Price Entity Price high: {self.price_high} land: {self.land} - ID:({self.id})"
