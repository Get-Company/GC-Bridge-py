from main.src.Controller.SW5_2.SW5_2ObjectController import SW5_2ObjectController
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity

from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity, BridgeOrderStateEntity
from main import db
from pprint import pprint
from datetime import datetime, date


class SW5_2OrderObjectController(SW5_2ObjectController):
    def __init__(self):

        super().__init__()

    def get_todays_open_orders(self):
        # orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(date(
        #     year=2023,
        #     month=5,
        #     day=9
        # ))
        orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate_and_enddate(
            startdate=date(year=2023, month=5, day=14),
            enddate=date(year=2023, month=5, day=15),
        )
        if len(orders) >= 1:
            for order in orders:
                order = SW5_2OrderObjectEntity().get_order_by_id(order['id'])
                customer = SW5_2CustomerObjectEntity().get_customer(order['customerId'])

                # 1. Sync the customer to the bridge
                self.sync_customer_to_bridge(sw5_customer=customer)
                # 2. Sync the order to the bridge
                # 3. Sync the status 'process' to the SW5 order
        else:
            print("No new order found in SW5")
            return None

    def sync_customer_to_bridge(self, sw5_customer):
        bridge_customer = BridgeCustomerEntity().map_sw5_to_db(sw5_customer)
        # Check if customer is already in db
        is_in_db = BridgeCustomerEntity().query.filter_by(erp_nr=bridge_customer.erp_nr).one_or_none()

        if is_in_db:
            print("Kunde gefunden, Update")
            for_db = is_in_db.update_entity(bridge_customer)
        else:
            print("Kunde neu, Insert")
            for_db = bridge_customer

        db.session.add(for_db)
        self.commit_with_errors()

        # Check if the addresses
        self.sync_addresses_to_bridge(sw5_customer=sw5_customer)

    def sync_addresses_to_bridge(self, sw5_customer):
        for index, address in sw5_customer["addresses"]:
            address = SW5_2CustomerObjectEntity().get_all_addresses_by_id(address["id"])
            bridge_address = BridgeCustomerAddressEntity().map_sw5_to_db(address=address)
            bridge_address.erp_ansnr = index
            bridge_address.erp_aspnr = 0
            is_in_db = BridgeCustomerAddressEntity().query.filter_by(api_id=address["id"])

            if is_in_db:
                print("Addresse gefunden, Update")
                for_db = is_in_db.update_entity

    """
    Atti
    """

    def get_orders(self, order_data):
        orders = {}
        order_id = order_data['id']  # extract order id
        orders[order_id] = {}  # initialize empty dict for the order

        total_amount = 0  # initialize total amount

        netto = order_data["net"]

        for key, value in order_data.items():
            if key == 'customerId':
                orders[order_id]['customer_id'] = value
            elif key == 'details':
                orders[order_id]['products'] = []  # initialize an empty list for products
                for order in value:  # go through every product
                    product = {}  # initialize empty dict for a product
                    product['product'] = order['articleNumber']

                    # Get absolutely the NETTO PRICE, regardless the country
                    if netto:
                        product['price'] = order['price']
                    else:
                        # Calc the netto price by the TaxRate of the article
                        # Round to 4 decimals, for the correct sum
                        netto_price = round(order['price']/(order["taxRate"]/100+1), 4)
                        product["price"] = netto_price

                    product['quantity'] = order['quantity']
                    product['total_price'] = round(product['price'] * order['quantity'], 2)
                    # Why would you calculate again?
                    total_amount = product['total_price']  # add product total price to total amount
                    orders[order_id]['products'].append(product)  # append the product to the list
            elif key == 'payment':
                orders[order_id]['payment_method'] = value['description']
            elif key == 'invoiceShippingNet':
                orders[order_id]['invoiceShippingNet'] = value

        orders[order_id]['total_amount'] = order_data["invoiceAmountNet"]  # add total amount to the order
        orders[order_id]["order_number"] = order_data["number"]
        orders[order_id]["shipping_method"] = order_data["shipping"]["country"]["iso"]
        return orders


    def insert_order_data(self, order_data):
        for order_id, data in order_data.items():
            customer_id = data['customer_id']
            total_amount = data['total_amount']
            payment_method = data['payment_method']
            shipping_costs = data['invoiceShippingNet']
            order_number = data["order_number"]
            shipping_method = data["shipping_method"]

            order_in_db = db.session.query(BridgeOrderEntity).filter_by(api_id=order_id).first()

            if order_in_db:
                continue

            customer_entity = db.session.query(BridgeCustomerEntity).filter_by(api_id=customer_id).first()

            order_entity = BridgeOrderEntity(
                api_id=order_id,
                purchase_date=datetime.now(),
                description='',
                total_price=total_amount,
                payment_method=payment_method,
                created_at=datetime.now(),
                edited_at=datetime.now(),
                customer_id=customer_entity.id,
                shipping_costs=shipping_costs,
                order_number=order_number,
                shipping_method=shipping_method
            )

            db.session.add(order_entity)
            db.session.commit()

            bridge_order_product_entity = db.Table('bridge_order_product_entity', db.metadata, autoload=True)

            for product_data in data['products']:
                product = db.session.query(BridgeProductEntity).filter_by(erp_nr=product_data['product']).first()
                print("Insert Product Data for Order:\n")
                pprint(product_data)
                pprint(product)
                db.session.execute(
                    bridge_order_product_entity.insert(),
                    {"order_id": order_entity.id, "product_id": product.id, "quantity": product_data['quantity'],
                     "unit_price": product_data['price'], "total_price": product_data['total_price']}
                )

            order = db.session.query(BridgeOrderEntity).filter_by(api_id=order_id).first()

            order_state_obj = BridgeOrderStateEntity()
            order_state_obj.order_id = order.id
            order_state_obj.payment_state = 0
            order_state_obj.shipping_state = 0
            order_state_obj.order_state = 0
            order_state_obj.created_at = datetime.now()
            order_state_obj.updated_at = datetime.now()

            db.session.add(order_state_obj)
            db.session.commit()




