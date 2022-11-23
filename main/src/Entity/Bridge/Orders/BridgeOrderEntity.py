from main import db
from datetime import datetime
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity

# Order Entity


class BridgeOrderEntity(db.Model):
    __tablename__ = "bridge_order_entity"

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.String(255), nullable=False)
    products = db.Column(db.String(255), nullable=False)
    order_date = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    """
    Relations
    """
    # Relation many - to -one
    customer = db.relationship(
        "BridgeCustomerEntity",
        back_populates="orders")
    customer_id = db.Column(db.Integer(), db.ForeignKey('bridge_customer_entity.id'))

    def update_entity(self, entity):
        """
        The entity is produced by ERP. Simply use the same names
        self.hans = entity.hans
        """
        self.id = entity.id
        self.api_id = entity.api_id
        self.products = entity.products
        self.order_date = entity.order_date
        self.description = entity.description

        return self

    # categories = db.relationship(
    #     "BridgeCategoryEntity",
    #     secondary=media_category,
    #     back_populates="categories"
