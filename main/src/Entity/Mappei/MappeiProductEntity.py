from main import db
from datetime import datetime
from main.src.Entity.Mappei.MappeiPriceEntity import *
import json

# Many-To-Many for Classei/Mappei
association_mappei_classei = db.Table('mappei_classei_product_entity',
                                      db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id')),
                                      db.Column('mappei_id', db.Integer, db.ForeignKey('mappei_product_entity.id'))
                                      )


# Make the mappeiProduct class
class MappeiProductEntity(db.Model):
    __tablename__ = 'mappei_product_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    nr = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.CHAR(), nullable=True)
    release_date = db.Column(db.DateTime(), nullable=True)
    last_mod = db.Column(db.DateTime(), default=datetime.now())

    # Prices as an archive one - to - many
    prices = db.relationship('MappeiPriceEntity', back_populates='product')

    # Mappei Relation many - to - many
    classei = db.relationship(
        'BridgeProductEntity',
        secondary=association_mappei_classei,
        back_populates='mappei',
        lazy='dynamic')

    def __repr__(self):
        return f"Mappei Product Entity {self.name}({self.nr})"

    def get_price(self, amount):
        price_high, price_low, price_quantity
        if int(amount) < int(self.prices.price_quantity):
            price = int(amount) * float(self.prices_price)
        elif int(amount) >= int(self.price_rebate_amount):
            price = int(amount) * float(self.price_rebate)

        if self.factor >= 1:
            price = float(price) / int(self.factor)

        return float(price)