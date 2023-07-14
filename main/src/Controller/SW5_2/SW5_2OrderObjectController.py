from sqlalchemy.exc import MultipleResultsFound

from main.src.Controller.SW5_2.SW5_2ObjectController import SW5_2ObjectController
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity

from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity, BridgeOrderStateEntity, order_product
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
        order_data = order_data["data"]
        order_id = order_data['id']  # extract order id
        orders[order_id] = {}  # initialize empty dict for the order

        total_amount = 0  # initialize total amount

        netto = order_data["net"]

        if order_data["shipping"] is None:
            order_data["shipping"] = order_data["billing"]

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
                        netto_price = round(order['price'] / (order["taxRate"] / 100 + 1), 4)
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
            try:
                customer_entity = db.session.query(BridgeCustomerEntity).filter_by(api_id=customer_id).one_or_none()
            except Exception as e:
                print("An error occurred while querying the customer entity:", str(e))

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

    """
    Flo 2.0
    """

    def upsert_order(self, order_data):
        order_details = SW5_2OrderObjectEntity().get_order_by_id(order_data["id"])
        order_in_db = None

        if order_details["success"] == True:

            try:
                order_in_db = BridgeOrderEntity.query.filter_by(
                    order_number=order_details["data"]["number"]).one_or_none()
            except Exception as e:
                print(f"Error on searching order:{order_details['data']['id']}. Multiple records found")
            # Update
            if order_in_db:
                print("Order found in DB: ", order_in_db.id)
                # Delete Product relations for the update:
                order_in_db.products = []

                pprint(order_details["data"]["number"])
                for product in order_details["data"]["details"]:
                    # Holen Sie die product_id aus Ihrer Produkttabelle
                    try:
                        product_in_db = BridgeProductEntity.query.filter_by(erp_nr=product["articleNumber"]).one_or_none()
                    except MultipleResultsFound as e:
                        print("Fehler bei der Suche nach dem Produkt: Mehrere Produkte gefunden für diese Artikelnummer", e)
                        product_in_db = None
                        break

                    if product_in_db is None:
                        print("Kein Produkt gefunden mit der Artikelnummer: ", product["articleNumber"])
                        break

                    if product_in_db:
                        net_price = self._set_netto_price(
                            net=order_details["data"]["net"],
                            product=product
                        )

                        print("Update order_product Table = OrderID:", order_in_db.id, "ProductID:", product_in_db.id)
                        # Führen Sie ein Update auf der order_product Tabelle durch
                        order_product_in_db = db.session.query(order_product).filter_by(
                            order_id=order_in_db.id,
                            product_id=product_in_db.id).first()

                        if order_product_in_db:
                            # Führen Sie ein Update auf der order_product Tabelle durch
                            db.session.execute(
                                order_product.update(). \
                                    where(order_product.c.order_id == order_in_db.id). \
                                    where(order_product.c.product_id == product_in_db.id). \
                                    values(
                                    quantity=product["quantity"],
                                    unit_price=net_price,
                                    total_price=(int(product["quantity"]) * net_price)
                                )
                            )
                        else:
                            # Fügen Sie einen neuen Eintrag in die order_product Tabelle ein
                            db.session.execute(
                                order_product.insert().values(
                                    order_id=order_in_db.id,
                                    product_id=product_in_db.id,
                                    quantity=product["quantity"],
                                    unit_price=net_price,
                                    total_price=(int(product["quantity"]) * net_price)
                                )
                            )

                self.commit_with_errors()

                return True
            # New
            else:
                print("New Order - ", order_details["data"]["number"])
                mapped_order = BridgeOrderEntity().map_sw5_to_db(order_details["data"])

                for product in order_details["data"]["details"]:
                    # Find the product in the db and add it to the order
                    product_in_db = BridgeProductEntity.query.filter_by(erp_nr=product["articleNumber"]).one_or_none()
                    if product_in_db:
                        mapped_order.products.append(product_in_db)

                    else:
                        print("Product not found")
                        pprint(product)

                # Add Customer to order
                try:
                    customer = BridgeCustomerEntity.query.filter_by(
                        api_id=order_details["data"]["customerId"]).one_or_none()
                except Exception as e:
                    print(f"Error on finding customer with id:{order_details['data']['customerId']} . {e}")
                    return False
                mapped_order.customer = customer

                order_state = BridgeOrderStateEntity()
                order_state.set_open_sw5()
                mapped_order.order_state = order_state

                db.session.add(mapped_order)
                self.commit_with_errors()

                # Get the current saved order from db and add extras to order_product
                try:
                    order_from_bridge = BridgeOrderEntity.query.filter_by(
                        order_number=order_details["data"]["number"]).one_or_none()
                except Exception as e:
                    print(
                        f'Error searching the order in DB by order_number: {order_details["data"]["number"]}, Error: {e}')
                    return False

                for product in order_details["data"]["details"]:
                    # Holen Sie die product_id aus Ihrer Produkttabelle
                    try:
                        product_entity = BridgeProductEntity.query.filter_by(
                            erp_nr=product["articleNumber"]).one_or_none()
                    except Exception as e:
                        print(f'Error searching the product in DB by erp_nr: {product["articleNumber"]}, Error: {e}')
                        return False

                    if product_entity:
                        if order_from_bridge is None:
                            print("Fehler: order_from_bridge ist None, konnte die Bestellung in der Datenbank nicht finden.")
                            return False

                        net_price = self._set_netto_price(
                            net=order_details["data"]["net"],
                            product=product
                        )

                        # Führen Sie ein Update auf der order_product Tabelle durch
                        order_product_in_db = db.session.query(order_product).filter_by(
                            order_id=order_from_bridge.id,
                            product_id=product_entity.id).first()

                        if order_product_in_db:
                            db.session.execute(
                                order_product.update(). \
                                    where(order_product.c.order_id == order_from_bridge.id). \
                                    where(order_product.c.product_id == product_entity.id). \
                                    values(
                                    quantity=product["quantity"],
                                    unit_price=net_price,
                                    total_price=(int(product["quantity"]) * net_price)
                                )
                            )
                        else:
                        # Fügen Sie einen neuen Eintrag in die order_product Tabelle ein
                            db.session.execute(
                                order_product.insert().values(
                                    order_id=order_from_bridge.id,
                                    product_id=product_entity.id,
                                    quantity=product["quantity"],
                                    unit_price=net_price,
                                    total_price=(int(product["quantity"]) * net_price)
                                )
                            )

                self.commit_with_errors()
                return True

        else:
            return None

    def _set_netto_price(self, net, product):
        # Get the net price - check order_details["data"]["net"] = 1
        if net == 0:
            tax_factor = (product["taxRate"] + 100) / 100  # (19+100)/100 = 1,19
            net_price = product["price"] / tax_factor
            return net_price
        elif net == 1:
            net_price = product["price"]
            return net_price
        else:
            print("Order Details field net is not 0 or 1 but, ", net)
            return False