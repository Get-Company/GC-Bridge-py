from main import db
import uuid
from datetime import datetime
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import *



class BridgeOrderStateEntity(db.Model):
    __tablename__ = 'bridge_order_state_entity'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
    payment_state = db.Column(db.Integer(), nullable=False)
    shipping_state = db.Column(db.Integer(), nullable=False)
    order_state = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.now())
    order_id = db.Column(db.Integer(), db.ForeignKey('bridge_order_entity.id'))

    """
    Relations
    """

    # Relation one-to-one
    order = db.relationship("BridgeOrderEntity", back_populates="order_state", uselist=False)

    def set_open(self):
        self.payment_state = 0
        self.shipping_state = 0
        self.order_state = 0
        return True

    def set_open_sw5(self):
        self.payment_state = 17
        self.shipping_state = 0
        self.order_state = 0
        return True
