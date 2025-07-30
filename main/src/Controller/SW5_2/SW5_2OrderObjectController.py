from loguru import logger
from sqlalchemy.exc import MultipleResultsFound

from main.src.Controller.SW5_2.SW5_2ObjectController import SW5_2ObjectController
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity

from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity, BridgeOrderStateEntity, order_product
from main import db
from datetime import datetime, date

from flask import current_app


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

        if order_details.get("success"):
            # Versuch, vorhandene Bestellung zu finden
            try:
                order_in_db = BridgeOrderEntity.query.filter_by(
                    order_number=order_details["data"]["number"]
                ).one_or_none()
            except Exception as e:
                current_app.logger.error(
                    "Error searching order %s: %s",
                    order_details["data"]["id"], e
                )

            # Update-Fall
            if order_in_db:
                current_app.logger.info("Order found in DB: %s", order_in_db.id)
                # Bestehende Produkt-Beziehungen entfernen
                order_in_db.products = []

                current_app.logger.debug(
                    "Processing update for order_number=%s",
                    order_details["data"]["number"]
                )
                for product in order_details["data"]["details"]:
                    # Produkt in DB suchen
                    try:
                        product_in_db = BridgeProductEntity.query.filter_by(
                            erp_nr=product["articleNumber"]
                        ).one_or_none()
                    except MultipleResultsFound as e:
                        current_app.logger.error(
                            "Multiple products found for articleNumber %s: %s",
                            product["articleNumber"], e
                        )
                        product_in_db = None
                        break

                    if not product_in_db:
                        current_app.logger.warning(
                            "No product found with articleNumber: %s",
                            product["articleNumber"]
                        )
                        break

                    net_price = self._set_netto_price(
                        net=order_details["data"]["net"],
                        product=product
                    )
                    current_app.logger.info(
                        "Updating order_product: order_id=%s, product_id=%s",
                        order_in_db.id, product_in_db.id
                    )

                    # Update oder Insert in order_product
                    order_product_in_db = db.session.query(order_product).filter_by(
                        order_id=order_in_db.id,
                        product_id=product_in_db.id
                    ).first()

                    if order_product_in_db:
                        db.session.execute(
                            order_product.update()
                            .where(order_product.c.order_id == order_in_db.id)
                            .where(order_product.c.product_id == product_in_db.id)
                            .values(
                                quantity=product["quantity"],
                                unit_price=net_price,
                                total_price=int(product["quantity"]) * net_price
                            )
                        )
                    else:
                        db.session.execute(
                            order_product.insert().values(
                                order_id=order_in_db.id,
                                product_id=product_in_db.id,
                                quantity=product["quantity"],
                                unit_price=net_price,
                                total_price=int(product["quantity"]) * net_price
                            )
                        )

                self.commit_with_errors()
                return True

            # New-Fall
            else:
                current_app.logger.info(
                    "New Order: order_number=%s",
                    order_details["data"]["number"]
                )
                mapped_order = BridgeOrderEntity().map_sw5_to_db(order_details["data"])

                for product in order_details["data"]["details"]:
                    try:
                        product_in_db = BridgeProductEntity.query.filter_by(
                            erp_nr=product["articleNumber"]
                        ).one_or_none()

                        if product_in_db:
                            mapped_order.products.append(product_in_db)
                        else:
                            # wenn kein Produkt gefunden wurde, als Warning loggen
                            logger.warning("Product not found: {}", product)
                            continue

                    except Exception:
                        # bei jeder Exception komplette Traceback und Produkt-Daten loggen
                        logger.exception("Error processing product: {}", product)
                        # je nach gewünschtem Verhalten hier weiterfahren oder neu werfen
                        continue

                # Customer hinzufügen
                try:
                    customer = BridgeCustomerEntity.query.filter_by(
                        api_id=order_details["data"]["customerId"]
                    ).one_or_none()
                except Exception as e:
                    current_app.logger.error(
                        "Error finding customer %s: %s",
                        order_details["data"]["customerId"], e
                    )
                    return False
                mapped_order.customer = customer

                # Status setzen und speichern
                order_state = BridgeOrderStateEntity()
                order_state.set_open_sw5()
                mapped_order.order_state = order_state

                db.session.add(mapped_order)
                self.commit_with_errors()

                # Neu gespeicherte Bestellung abrufen
                try:
                    order_from_bridge = BridgeOrderEntity.query.filter_by(
                        order_number=order_details["data"]["number"]
                    ).one_or_none()
                except Exception as e:
                    current_app.logger.error(
                        "Error searching new order %s: %s",
                        order_details["data"]["number"], e
                    )
                    return False

                for product in order_details["data"]["details"]:
                    try:
                        product_entity = BridgeProductEntity.query.filter_by(
                            erp_nr=product["articleNumber"]
                        ).one_or_none()
                    except Exception as e:
                        current_app.logger.error(
                            "Error searching product %s: %s",
                            product["articleNumber"], e
                        )
                        return False

                    if not product_entity:
                        continue

                    if order_from_bridge is None:
                        current_app.logger.error(
                            "order_from_bridge is None for order_number: %s",
                            order_details["data"]["number"]
                        )
                        return False

                    net_price = self._set_netto_price(
                        net=order_details["data"]["net"],
                        product=product
                    )

                    order_product_in_db = db.session.query(order_product).filter_by(
                        order_id=order_from_bridge.id,
                        product_id=product_entity.id
                    ).first()

                    if order_product_in_db:
                        db.session.execute(
                            order_product.update()
                            .where(order_product.c.order_id == order_from_bridge.id)
                            .where(order_product.c.product_id == product_entity.id)
                            .values(
                                quantity=product["quantity"],
                                unit_price=net_price,
                                total_price=int(product["quantity"]) * net_price
                            )
                        )
                    else:
                        db.session.execute(
                            order_product.insert().values(
                                order_id=order_from_bridge.id,
                                product_id=product_entity.id,
                                quantity=product["quantity"],
                                unit_price=net_price,
                                total_price=int(product["quantity"]) * net_price
                            )
                        )

                self.commit_with_errors()
                return True

        return None

    def _set_netto_price(self, net, product):
        if net == 0:
            tax_factor = (product["taxRate"] + 100) / 100
            return product["price"] / tax_factor
        elif net == 1:
            return product["price"]
        else:
            current_app.logger.warning("Unexpected 'net' value: %s", net)
            return False
