import uuid
from main import db
from datetime import datetime


# Make the price class
class BridgePriceEntity(db.Model):
    __tablename__ = 'bridge_price_entity'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    price = db.Column(db.Float, nullable=False)
    rebate_quantity = db.Column(db.Integer, nullable=False)
    rebate_price = db.Column(db.Float, nullable=False)
    special_price = db.Column(db.Float, nullable=True)
    special_start_date = db.Column(db.DateTime, nullable=True)
    special_end_date = db.Column(db.DateTime, nullable=True)
    is_current = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    # Price Product Relation one - to - one
    # Todo: Make a history of prices. The field is_current should show the current price.
    product = db.relationship(
        "BridgeProductEntity",
        back_populates="prices")
    product_id = db.Column(db.Integer(), db.ForeignKey('bridge_product_entity.id'), unique=True)

    def update_entity(self, entity):
        self.price = entity.price
        self.rebate_quantity = entity.rebate_quantity
        self.rebate_price = entity.rebate_price
        self.special_price = entity.special_price
        self.special_start_date = entity.special_start_date
        self.special_end_date = entity.special_end_date
        self.is_current = entity.is_current

        return self

    def map_erp_to_db(self, erp_entity,price_level=0, special_price_level=0):
        """
        There are a lot of Price Levels:
        VK0.Preis, VK1.Preis aso
        VK0.Rab0.Pr, VK0.Rab1.Pr aso.
        You can adjust the parameters, to get the amount you need. Standard is Vk0 and Rab0
        :param price_level:
        :param special_price_level_1:
        :param special_price_level_0:
        :param erp_entity:
        :param special_price_level:
        :return:
        """
        vk = f"VK{price_level}."  # <-- Mind the dot at the end!
        rab = f"Rab{special_price_level}."  # <-- Mind the dot at the end!
        self.price = erp_entity.get_(vk + "Preis")
        self.rebate_quantity = erp_entity.get_(vk + rab + "Mge")
        self.rebate_price = erp_entity.get_(vk + rab + "Pr")
        self.special_price = erp_entity.get_(vk + "SPr")
        self.special_start_date = erp_entity.get_(vk + "SVonDat").replace(tzinfo=None)
        self.special_end_date = erp_entity.get_(vk + "SBisDat").replace(tzinfo=None)
        self.is_current = 1

        return self

    def get_current_prices(self, entity):
        """
        Returns a list of all current prices.

        :return: List of current prices.
        :rtype: list of BridgePriceEntity
        """
        try:
            current_prices = BridgePriceEntity.query.filter_by(is_current=True, product_id=entity.id).all()
            if not current_prices:
                # No current prices found
                print(f"No current prices found for {entity.erp_nr}")
                return False
            return current_prices
        except Exception as e:
            # Handle exception
            print(f"Error while getting current prices: {entity.erp_nr}")
            return None

    def update_current_prices(self, new_prices, product):
        """Updates is_current flag for prices on a product.

        Sets is_current flag to True for new_prices and to False for all other prices
        for the same product.

        Args:
            new_prices (list[BridgePriceEntity]): List of new prices to set as
                current.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            # Find all prices for the product that are not in the new prices list
            old_prices = BridgePriceEntity.query.filter(
                BridgePriceEntity.product_id == self.product.id,
                BridgePriceEntity.id.notin_([p.id for p in new_prices])
            ).all()

            # Set is_current flag to False for old prices
            for price in old_prices:
                price.is_current = False
                db.session.add(price)

            # Set is_current flag to True for new prices
            for price in new_prices:
                price.is_current = True
                db.session.add(price)

            # Set update timestamps for all prices
            for price in old_prices + new_prices:
                price.updated_at = datetime.now()
                db.session.add(price)

            # Commit changes to the database
            db.session.commit()

            return True

        except Exception as e:
            # Log error
            print(f"Error updating prices for product {self.product.erp_nr}: {e}")
            db.session.rollback()

            return False
