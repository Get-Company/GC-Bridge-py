from sqlalchemy import and_

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
    description = db.Column(db.String(4096), nullable=True)
    total_price = db.Column(db.Float(), nullable=False)
    shipping_costs = db.Column(db.Float(), nullable=False)
    payment_method = db.Column(db.String(255), nullable=True)
    shipping_method = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=False)
    order_number = db.Column(db.String(255), nullable=True)

    """
    Relations
    """
    # Relation one - to - one
    order_state = db.relationship("BridgeOrderStateEntity", uselist=False, back_populates="order")

    # Relation many - to - one
    customer = db.relationship(
        "BridgeCustomerEntity",
        uselist=False,
        back_populates="orders")

    customer_id = db.Column(db.Integer(), db.ForeignKey('bridge_customer_entity.id'))

    # Order Products Relation many - to - many
    products = db.relationship(
        'BridgeProductEntity',
        secondary=order_product,
        back_populates='orders',
        lazy='joined')

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

        product_list = []
        for product in order_products:
            product_list.append({
                'product_id': product[0],
                'quantity': product[1],
                'unit_price': product[2],
                'total_price': product[3]
            })

        return product_list

    def add_order_product_fields_to_product(self):
        for product in self.products:
            order_product_found = db.session.query(
                order_product.c.quantity,
                order_product.c.unit_price,
                order_product.c.total_price
            ).filter(
                and_(
                    order_product.c.product_id == product.id,
                    order_product.c.order_id == self.id
                )
            ).one_or_none()

            product.quantity = order_product_found.quantity
            product.unit_price = order_product_found.unit_price
            product.total_price = order_product_found.total_price

        return True


    def get_open_orders(self):
        """
        Query the database to get all orders with payment_state, shipping_state, and order_state equal to 0 (new orders).
        :return: A list of BridgeOrderEntity objects.
        """
        try:
            new_orders = BridgeOrderEntity.query.join(BridgeOrderStateEntity).filter(
                BridgeOrderStateEntity.payment_state == 0,
                BridgeOrderStateEntity.shipping_state == 0,
                BridgeOrderStateEntity.order_state == 0
            ).all()

            self.new_orders = new_orders
        except Exception as e:
            print(f"Error querying new orders: {str(e)}")

    def map_sw5_to_db(self, order):
        self.api_id = order["id"]
        self.purchase_date = datetime.strptime(order["orderTime"], "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
        self.total_price = order["invoiceAmountNet"]
        self.shipping_costs = order["invoiceShippingNet"]
        self.payment_method = order["payment"]["description"]
        self.created_at = datetime.now()
        self.edited_at = datetime.now()
        self.erp_order_id = "SW5_" + str(order["id"])
        self.order_number = order["number"]
        self.shipping_method = order["billing"]["country"]["iso"]
        self.description = order["customerComment"]

        return self

    def __repr__(self):
        return f"" \
               f"Order: {self.api_id} " \
               f"from: {self.purchase_date}. " \
               f"Total: {self.total_price}, " \
               f"Shipping:{self.shipping_costs} - Land: {self.shipping_method} " \
               f"ERP Order ID: {self.erp_order_id} - Order Number:{self.order_number} " \
               f"Payment: {self.payment_method}"











