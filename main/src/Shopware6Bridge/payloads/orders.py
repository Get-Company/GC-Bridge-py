from sqlite3 import IntegrityError

from sqlalchemy import insert
from sqlalchemy.orm import joinedload
from main.src.Entity.Bridge.Orders.BridgeOrderStateEntity import *

from main.src.Shopware6Bridge.connectors.dbconnector import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import *
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import *
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import *
from main.src.Shopware6Bridge.db_requests.categories import *
from main.src.Shopware6Bridge.payloads.customers import CustomerPayload
from main.src.Shopware6Bridge.sync.sw6_request import *
from main.src.Entity.Bridge.Price.BridgePriceEntity import *
from main.src.Shopware6Bridge.db_requests.customers import *
from main.src.Shopware6Bridge.sync.sw6_request import *
from datetime import datetime
r = Requests()

#
# def upload_all_new_orders_from_SW6_to_BRIDGE(orders):
#     for api_id, order_data in orders.items():
#         customer = sql_session.query(BridgeCustomerEntity).filter_by(api_id=order_data['customerID']).first()
#         customer_id = customer.id
#         order_date_str = order_data['orderDate'].replace('Z', '+00:00')
#         order_date = datetime.fromisoformat(order_date_str)
#         description = None
#         order = BridgeOrderEntity(api_id=api_id,
#                                   purchase_date=order_date,
#                                   description=description,
#                                   edited_at=order_date,
#                                   customer_id=customer_id)
#         sql_session.add(order)
#         sql_session.commit()
#
#         for product in order_data['products']:
#             product_id = product['product_id']
#             quantity = product['quantity']
#             unit_price = product['unit_price']
#             total_price = product['total_price']
#             producte = sql_session.query(BridgeProductEntity).filter_by(api_id=peroduct_id).first()
#             orders = sql_session.query(BridgeOrderEntity).filter_by(api_id=api_id).first()
#             orders.products.append(producte)
#             sql_session.add(orders)
#             sql_session.commit()

def upload_all_new_orders_from_SW6_to_BRIDGE(orders):
    for api_id, order_data in orders.items():
        order_in_db = sql_session.query(BridgeOrderEntity).filter_by(api_id=api_id).first()

        if order_in_db:
            continue

        payment_method = order_data["payment_method"]
        customer = sql_session.query(BridgeCustomerEntity).filter_by(api_id=order_data['customerID']).first()
        customer_id = customer.id
        print(order_data['orderDateTime'])
        order_date_str = order_data['orderDateTime'].replace('Z', '+00:00')
        positionprice = order_data['total'][0]['price']
        order_date = datetime.fromisoformat(order_date_str)
        description = None

        # Create a new instance of BridgeOrderStateEntity
        order_state = BridgeOrderStateEntity()
        order_state.payment_state = 0
        order_state.shipping_state = 0
        order_state.order_state = 0

        # Create the BridgeOrderEntity instance
        order = BridgeOrderEntity(api_id=api_id,
                                  purchase_date=order_date,
                                  description=description,
                                  edited_at=order_date,
                                  customer_id=customer_id,
                                  total_price=positionprice,
                                  payment_method=payment_method)

        # Associate the order with the order_state
        order.order_state = order_state

        # Associate the order_state with the order
        order_state.order = order

        sql_session.add(order)
        sql_session.add(order_state)
        sql_session.commit()



        bridge_order_product_entity = db.Table('bridge_order_product_entity', db.metadata, autoload=True)

        for product in order_data['products']:
            product_id = product['product_id']
            quantity = product['quantity']
            unit_price = product['unit_price']
            total_price = product['total_price']
            product_entity = sql_session.query(BridgeProductEntity).filter_by(api_id=product_id).first()

            sql_session.execute(
                bridge_order_product_entity.insert(),
                {"order_id": order.id, "product_id": product_entity.id, "quantity": quantity,
                 "unit_price": unit_price, "total_price": total_price})

            sql_session.commit()






# upload_all_new_orders_from_SW6_to_BRIDGE(r.get_all_orders_from_SW6())

# order_id = 3
#
# order = sql_session.query(BridgeOrderEntity).options(joinedload(BridgeOrderEntity.products))\
#             .filter_by(id=order_id)\
#             .first()
#
# for order_product in order.order_product:
#     product_id = order_product.product_id
#     quantity = order_product.quantity
#     unit_price = order_product.unit_price
#     total_price = order_product.total_price
#
#     product = sql_session.query(BridgeProductEntity).filter_by(id=product_id).first()
#     product_name = product.name
#
#     print(f"Product: {product_name}, Quantity: {quantity}, Unit Price: {unit_price}, Total Price: {total_price}")