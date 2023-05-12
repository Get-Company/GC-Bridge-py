from main.src.Controller.SW5_2.SW5_2ObjectController import SW5_2ObjectController
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity

from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderStateEntity
from main import db
from pprint import pprint
from datetime import datetime, date


class SW5_2OrderObjectController(SW5_2ObjectController):
    def __init__(self):

        super().__init__()

    def get_todays_open_orders(self):
        orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(date(
            year=2023,
            month=5,
            day=9
        ))
        if len(orders) >= 1:
            for order in orders:
                order = SW5_2OrderObjectEntity().get_order_by_id(order['id'])
                customer = SW5_2CustomerObjectEntity().get_customer(order['customerId'])

                # 1. Sync the customer to the bridge
                pprint(customer)
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





