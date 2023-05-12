from main import db
from datetime import datetime
import pprint
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Orders.BridgeOrderStateEntity import BridgeOrderStateEntity

# Many-To-Many for Order/Product
order_product = db.Table('bridge_order_product_entity',
                         db.Column('id', db.Integer(), primary_key=True, nullable=False),
                         db.Column('order_id', db.Integer, db.ForeignKey('bridge_order_entity.id')),
                         db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id')),
                         db.Column('quantity', db.Integer()),
                         db.Column('unit_price', db.Float()),
                         db.Column('total_price', db.Float())
                         )

# Order Entity
class BridgeOrderEntity(db.Model):
    __tablename__ = "bridge_order_entity"

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False)
    erp_order_id = db.Column(db.String(255), nullable=True)
    purchase_date = db.Column(db.DateTime(), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    total_price = db.Column(db.Float(), nullable=False)
    payment_method = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=False)

    """
    Relations
    """
    # Relation one - to - one
    order_state = db.relationship("BridgeOrderStateEntity", uselist=False, back_populates="order")

    # Relation many - to - one
    customer = db.relationship(
        "BridgeCustomerEntity",
        back_populates="orders")

    customer_id = db.Column(db.Integer(), db.ForeignKey('bridge_customer_entity.id'))

    # Order Products Relation many - to - many
    products = db.relationship(
        'BridgeProductEntity',
        secondary=order_product,
        back_populates='orders',
        lazy='dynamic')




    def update_entity(self, entity):
        """
        The entity is produced by ERP. Simply use the same names
        self.hans = entity.hans
        """
        self.id = entity.id
        self.api_id = entity.api_id
        self.description = entity.description
        self.edited_at = datetime.now()

        return self

    def get_order_products(self):
        """
        Returns a list of dictionaries containing product information (id, quantity, unit_price, total_price)
        for all products associated with this order.
        """
        order_products = db.session.query(
            order_product.c.product_id,
            order_product.c.quantity,
            order_product.c.unit_price,
            order_product.c.total_price
        ).filter(
            order_product.c.order_id == self.id
        ).all()

        products_list = []
        for product in order_products:
            product.append({
                'product_id': product[0],
                'quantity': product[1],
                'unit_price': product[2],
                'total_price': product[3]
            })

        return True












