from main import db
from datetime import datetime
import json
from sqlalchemy import update
from main.src.Entity.Mappei.MappeiProductEntity import MappeiProductEntity, association_mappei_classei
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Repository.functions_repository import parse_european_number_to_float

# Many-To-Many for Product/Category
product_category = db.Table('bridge_product_category_entity',
                            db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id'),
                                      primary_key=True),
                            db.Column('category_id', db.Integer, db.ForeignKey('bridge_category_entity.id'),
                                      primary_key=True)
                            )


# TODO: Make the mapping a Method of the classes, since we have the "self" variabble

# Make the product class
class BridgeProductEntity(db.Model):
    __tablename__ = 'bridge_product_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.String(255), nullable=True)
    api_id = db.Column(db.CHAR(36), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.JSON(), nullable=True)
    description = db.Column(db.CHAR(), nullable=True)
    price = db.Column(db.Float(), nullable=True)
    price_rebate_amount = db.Column(db.Integer(), nullable=True)
    price_rebate = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer(), nullable=False)
    factor = db.Column(db.Integer(), nullable=True)
    min_purchase = db.Column(db.Integer(), nullable=True)
    purchase_unit = db.Column(db.Integer(), nullable=True)

    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.now())

    # Translation for Product one - to - many
    translations = db.relationship('BridgeProductTranslationEntity', backref='product')

    # Categories Products Relation many - to - many
    categories = db.relationship(
        'BridgeCategoryEntity',
        secondary=product_category,
        back_populates='products',
        lazy='dynamic')

    # Mappei Relation many - to - many
    mappei = db.relationship(
        'MappeiProductEntity',
        secondary=association_mappei_classei,
        back_populates='classei',
        lazy='dynamic',
        cascade="all, delete")

    # Tax Product Relation one - to - many
    tax_id = db.Column(db.Integer, db.ForeignKey('bridge_tax_entity.id'))
    tax = db.relationship("BridgeTaxEntity", back_populates="products")

    def __repr__(self):
        return f"Product Entity {self.name}({self.erp_nr})"

    def update_entity(self, entity):
        """
        The entity is produced by ERP. Simply use the same names
        self.hans = entity_hans
        """
        self.erp_nr = entity.erp_nr
        if entity.api_id:
            self.api_id = entity.api_id
        self.name = entity.name
        self.image = entity.image
        self.description = entity.description
        self.price = entity.price
        self.price_rebate_amount = entity.price_rebate_amount
        self.price_rebate = entity.price_rebate
        self.stock = entity.stock
        self.factor = entity.factor
        self.min_purchase = entity.min_purchase
        self.purchase_unit = entity.purchase_unit
        return True

    def update_category(self, category_entity):
        self.categories = [category_entity]
        return True

    def check_if_prod_cat(self, cat_id, prod_id):
        """
        Checks for a relationship in the assoc table
        :param cat_id:
        :param prod_id:
        :return: bool
        """
        prod_cat = db.session.query(product_category).filter_by(
            product_id=prod_id,
            category_id=cat_id
        ).first()
        if prod_cat is None:
            return False
        else:
            return prod_cat

    def get_price(self, amount):
        if int(amount) < int(self.price_rebate_amount):
            price = int(amount) * float(self.price)
        elif int(amount) >= int(self.price_rebate_amount):
            price = int(amount) * float(self.price_rebate)

        if self.factor >= 1:
            price = float(price) / int(self.factor)

        return float(price)


def map_product_erp_to_bridge_db(dataset, img=None):
    """
    Maps the fields from ERP to the Bridge DB
    :param dataset: object Dataset
    :param img: JSON Object Like {"Bild1": "/some/path/to/image/image1.jpg", ...}
    :return: object Entity with translations as array
    """
    # Mapping the Entity
    entity = BridgeProductEntity(
        erp_nr=dataset.Fields.Item("ArtNr").AsString,
        api_id=0,
        name=dataset.Fields.Item("KuBez1").AsString,
        image=img,  # JSON Object Like {"Bild1": "/some/path/to/image/image1.jpg", ...}
        description=dataset.Fields.Item("Bez5").Text,
        stock=99999,
        price=parse_european_number_to_float(dataset.Fields.Item("Vk0.Preis").AsString),
        price_rebate_amount=dataset.Fields.Item("Vk0.Rab0.Mge").AsString,
        price_rebate=parse_european_number_to_float(dataset.Fields("Vk0.Rab0.Pr").AsString),
        factor=dataset.Fields.Item("Sel6").AsString,
        min_purchase=dataset.Fields.Item("Sel10").AsString,
        purchase_unit=dataset.Fields.Item("Sel11").AsString
    )
    print('This is the "ArtKat1" : "%s"' % dataset.Fields.Item("ArtKat1").AsInteger)

    return entity


# Make the translation class
class BridgeProductTranslationEntity(db.Model):
    __tablename__ = 'bridge_product_translation_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language_iso = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.CHAR(), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.now())

    # Translation for Product
    product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id'))

    def update_entity(self, entity):
        self.language_iso = entity.language_iso
        self.name = entity.name
        self.image = entity.image
        self.description = entity.description
        return True


def map_product_erp_language_to_bridge(dataset, entity, language, img=None):
    # Translating the Entity with the value lang
    translation = BridgeProductTranslationEntity(
        language_iso=language,
        name=dataset.Fields.Item("KuBez1").AsString,
        image=img,
        description=dataset.Fields.Item("Bez1").Text
        # product=entity
    )
    return translation
