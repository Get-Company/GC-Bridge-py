import re
import uuid
import sys
from typing import Union

from main import db
from datetime import datetime
import json
from slugify import slugify

from main.src.Entity.Bridge.Media.BridgeMediaEntity import *
from main.src.Entity.Mappei.MappeiProductEntity import MappeiProductEntity, association_mappei_classei
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import *
from main.src.Repository.functions_repository import parse_european_number_to_float

# Many-To-Many for Product/Category
product_category = db.Table('bridge_product_category_entity',
                            db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id'),
                                      primary_key=True),
                            db.Column('category_id', db.Integer, db.ForeignKey('bridge_category_entity.id'),
                                      primary_key=True)
                            )


# Make the product class
class BridgeProductEntity(db.Model):
    __tablename__ = 'bridge_product_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.String(255), nullable=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    name = db.Column(db.String(255), nullable=True)
    name_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(4294967295), nullable=True)
    description_short = db.Column(db.Text(4294967295), nullable=True)
    image = db.Column(db.JSON(), nullable=True)
    stock = db.Column(db.Integer(), nullable=False)
    factor = db.Column(db.Integer(), nullable=True)
    min_purchase = db.Column(db.Integer(), nullable=True)
    purchase_unit = db.Column(db.Integer(), nullable=True)
    unit = db.Column(db.String(255), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.today())
    wshopkz = db.Column(db.Boolean(), nullable=True)
    shipping_cost_per_bundle = db.Column(db.Float(), nullable=True)
    shipping_bundle_size = db.Column(db.Integer(), nullable=True)
    sort = db.Column(db.Integer(), nullable=True)

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

    # Price Products Relation one - to - one
    prices = db.relationship(
        'BridgePriceEntity',
        uselist=False,  # It's a one-to-one, is one-to-many a better idea?
        back_populates="product",
        cascade="all, delete")

    # Tax one - to - one
    tax_id = db.Column(db.Integer, db.ForeignKey('bridge_tax_entity.id'))
    tax = db.relationship('BridgeTaxEntity')

    # Media Relation many - to - many
    medias = db.relationship(
        'BridgeMediaEntity',
        secondary=media_prod,
        back_populates="products",
        cascade="all, delete"
    )

    # Order Relation many - to - many
    orders = db.relationship(
        'BridgeOrderEntity',
        secondary=order_product,
        back_populates="products"
    )

    def __repr__(self):
        return f"Product Entity {self.name}({self.erp_nr})"

    def update_entity(self, entity):
        """
        The entity is produced by ERP. Simply use the same names
        self.hans = entity.hans
        """
        self.erp_nr = entity.erp_nr
        self.image = entity.image
        self.name = entity.name
        self.description = entity.description
        self.description_short = entity.description_short
        self.stock = entity.stock
        self.factor = entity.factor
        self.min_purchase = entity.min_purchase
        self.purchase_unit = entity.purchase_unit
        self.unit = entity.unit
        self.wshopkz = entity.wshopkz
        self.shipping_cost_per_bundle = entity.shipping_cost_per_bundle
        self.shipping_bundle_size = entity.shipping_bundle_size

        return self

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def map_erp_to_db(self, erp_entity: ERPArtikelEntity):
        self.erp_nr = erp_entity.get_("ArtNr")
        self.name = erp_entity.get_("KuBez5")

        # Make it websafe
        txt = erp_entity.get_("KuBez5")  # Get the name
        regex_pattern = r'[^-a-zA-Z0-9_/]+'  # Search for Chars we want to keep
        umlaute = [
            ['Ä', 'AE'],
            ['ä', 'ae'],
            ['Ö', 'OE'],
            ['ö', 'oe'],
            ['Ü', 'UE'],
            ['ü', 'ue']
        ]
        slug = slugify(
            txt,
            regex_pattern=regex_pattern,
            replacements=umlaute,
            lowercase=False)  # Do the magic
        self.name_url = slug

        self.image = erp_entity.get_images()
        self.description = erp_entity.get_("Bez5")
        self.description_short = erp_entity.get_("Bez2")

        self.stock = erp_entity.get_("LagMge")

        if erp_entity.get_("Sel6"):
            self.factor = erp_entity.get_("Sel6")
        else:
            self.factor = None
        self.min_purchase = erp_entity.get_("Sel10")
        self.purchase_unit = erp_entity.get_("Sel11")
        self.wshopkz = erp_entity.get_("WShopKz")
        self.created_at = datetime.now()
        self.unit = erp_entity.get_("Einh")
        self.erp_ltz_aend = erp_entity.get_("LtzAend").replace(tzinfo=None)
        # Always keep api_ids
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        self.shipping_cost_per_bundle = erp_entity.get_("Sel70")  # Frachtkostenpauschale
        self.shipping_bundle_size = erp_entity.get_("Sel71")  # Frachtkostenaufschlag pro Stück

        self.sort = erp_entity.get_("Sel19")  # Selektions-Feld Sortierung

        # Relations are set in the Bridge2ObjectProductController

        return self

    def get_special_price(self):
        """
        Check if there is a special price for this product and return the special price if it exists,
        otherwise return False.

        :return: float or False
        """
        now = datetime.now()
        if self.prices.special_price and self.prices.special_start_date <= now <= self.prices.special_end_date:
            return self.prices.special_price
        return False

    def get_current_price(self):
        """
        Returns the current price of the product based on the date.
        If there is a special price, it returns that instead of the regular price.
        """
        today = datetime.now()
        if self.prices.special_price and self.prices.special_start_date <= today <= self.prices.special_end_date:
            return self.prices.special_price
        else:
            return self.prices.price

        return None

    def get_list_price(self):
        """
        Returns the current price of the product.
        """
        return self.prices.price

    def get_shipping_cost(self, shipping: Union[str, float] = '5,95', no_shipping_from: float = 99.0) -> Union[
        str, float]:
        """
        Returns the shipping cost for this BridgeProductEntity object.
        If the product has a fixed shipping cost per bundle, it returns that value.
        Otherwise, it checks the current price of the product and returns the shipping cost
        if the price is below the threshold for free shipping.

        Args:
            shipping (str or float, optional): The shipping cost to return if applicable.
                If a string, should be in the format "x,yz" with the decimal separator as a comma.
                If a float, should be the shipping cost in EUR.
                Defaults to '5,95'.
            no_shipping_from (float, optional): The price threshold for free shipping.
                Defaults to 99.0.

        Returns:
            str or float: The shipping cost if applicable, or 0 if the price is above the threshold for free shipping.
                If the shipping cost is returned as a float, it will be rounded to two decimal places.
        """
        if self.shipping_cost_per_bundle:
            # If the product has a fixed shipping cost per bundle, return that value.
            return self.shipping_cost_per_bundle
        elif self.prices:
            # If the product has at least one price, check the current price and return the shipping cost if applicable.
            current_price = self.get_current_price()
            # if there is a factor
            if self.factor:
                current_price = current_price / self.factor
            if current_price <= no_shipping_from:
                # If the current price is below the threshold for free shipping, return the shipping cost.
                if isinstance(shipping, str):
                    # If the shipping cost is given as a string, convert it to a float with comma as decimal separator.
                    shipping = float(shipping.replace(',', '.'))
                return round(shipping, 2)  # Round to two decimal places.
        # If the product has no fixed shipping cost per bundle and no prices, return 0.
        return 0

    def get_unit_price(self, order):
        unit_price = db.session.query(
            order_product.c.unit_price,
        ).filter(
            order_product.c.product_id == self.id,
            order_product.c.order_id == order.id
        ).scalar()

        return unit_price


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
