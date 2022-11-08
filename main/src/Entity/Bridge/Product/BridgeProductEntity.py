import uuid
import sys
from main import db
from datetime import datetime
import json
from sqlalchemy import update
from main.src.Entity.Mappei.MappeiProductEntity import MappeiProductEntity, association_mappei_classei
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity
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
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.JSON(), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    price = db.Column(db.Float(), nullable=True)
    price_rebate_amount = db.Column(db.Integer(), nullable=True)
    price_rebate = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer(), nullable=False)
    factor = db.Column(db.Integer(), nullable=True)
    min_purchase = db.Column(db.Integer(), nullable=True)
    purchase_unit = db.Column(db.Integer(), nullable=True)
    unit = db.Column(db.String(255), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.today())
    wshopkz = db.Column(db.Boolean(), nullable=True)

    created_at = db.Column(db.DateTime(), nullable=True, default=' ')

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

    # Tax one - to - one
    tax_id = db.Column(db.Integer, db.ForeignKey('bridge_tax_entity.id'))
    tax = db.relationship('BridgeTaxEntity')

    def __repr__(self):
        return f"Product Entity {self.name}({self.erp_nr})"

    def update_entity(self, entity):
        """
        The entity is produced by ERP. Simply use the same names
        self.hans = entity.hans
        """
        self.erp_nr = entity.erp_nr
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
        self.unit = entity.unit
        self.wshopkz = entity.wshopkz
        return True

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def map_erp_to_db(self, erp_product: ERPArtikelEntity, img=None):
        self.erp_nr = erp_product.get_("ArtNr"),
        # Always keep api_ids
        if not self.api_id:
            self.api_id = uuid.uuid4().hex
        self.name = erp_product.get_("KuBez1"),
        self.image = img,  # JSON Object Like {"Bild1": "/some/path/to/image/image1.jpg", ...}
        self.description = erp_product.get_("Bez5"),
        self.stock = 99999,
        self.price = parse_european_number_to_float(erp_product.get_("Vk0.Preis")),
        self.price_rebate_amount = erp_product.get_("Vk0.Rab0.Mge"),
        self.price_rebate = parse_european_number_to_float(erp_product.get_("Vk0.Rab0.Pr")),
        self.created_at = datetime.now()

        """
        Also reset all relations and set them anew
        """
        # Categories
        if 'BridgeCategoryEntity' not in sys.modules:
            from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
        self.categories = []
        for i in range(1, 11):
            search = "erp_product.get_('ArtKat" + str(i) + "')"
            cat_id = eval(search)
            # Categories must be in db, error
            if cat_id > 0:
                try:
                    cat_db = BridgeCategoryEntity().query.filter_by(erp_nr=cat_id).first()
                    self.categories.append(cat_db)
                except:
                    print("A Problem with cat_nr: %s for prod_nr: %s" % (cat_id, self.erp_nr))
                    db.session.rollback()
                    pass

        # Tax
        tax = BridgeTaxEntity().query.filter_by(steuer_schluessel=erp_product.get_('StSchl')).first()
        self.tax = tax

        return self

    def get_price(self, amount):
        """
        Get the price for the given amount
        :param amount:
        :return: float
        """
        if int(amount) < int(self.price_rebate_amount):
            price = int(amount) * float(self.price)
        elif int(amount) >= int(self.price_rebate_amount):
            price = int(amount) * float(self.price_rebate)

        if self.factor >= 1:
            price = float(price) / int(self.factor)

        return float(price)



# Make the translation class
class BridgeProductTranslationEntity(db.Model):
    __tablename__ = 'bridge_product_translation_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language_iso = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
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
