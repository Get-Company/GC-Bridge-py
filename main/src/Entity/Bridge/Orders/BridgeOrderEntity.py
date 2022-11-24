from main import db
from datetime import datetime
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity

# Order Entity


class BridgeOrderEntity(db.Model):
    __tablename__ = "bridge_order_entity"

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False)
    purchase_date = db.Column(db.DateTime(), nullable=False)
    state = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=False)

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
        self.state = entity.state
        self.description = entity.description
        self.edited_at = datetime.now()

        return self
