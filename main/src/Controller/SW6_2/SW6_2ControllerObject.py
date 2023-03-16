from pprint import pprint

from main.src.Entity.SW6_2.SW6_2ObjectEntity import SW6_2ObjectEntity
from main import db

import uuid
from pprint import pprint

from sqlalchemy import exists

# Entities
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

# Controller
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerController import Bridge2ObjectCustomerController

from datetime import datetime

from main.src.Repository.functions_repository import parse_a_date_time


class SW6_2ControllerObject():
    def __init__(self):
        self.api = SW6_2ObjectEntity()
        self.bridge_synchronize_entity = BridgeSynchronizeEntity().get_entity_by_id_1()

    def insert_init(self):
        # self.api.delete_all_products()
        # self.api.delete_all_categories()
        # self.api.delete_all_taxes()
        # self.api.delete_all_customers()

        self.upsert_taxes()
        self.upsert_categories()
        self.upsert_products()

    """
    Init functions for a new shop
    """
    def create_saleschannels(self):
        """
        We need 3 sales channels
        DE_de
        CH_de
        IT_de | IT_it
        :return:
        """
        self.api.create_saleschannel()

    def upsert_categories(self):
        cats = db.session.query(BridgeCategoryEntity).order_by(BridgeCategoryEntity.erp_nr_parent.asc())

        for cat in cats:
            self.api.upsert_category(category=cat)

        for cat in cats:
            self.api.upsert_category(category=cat, with_parent=True)

        self.bridge_synchronize_entity.sw6_category_sync_date = datetime.now()
        db.session.add(self.bridge_synchronize_entity)
        db.session.commit()

    def upsert_taxes(self):
        taxes = BridgeTaxEntity.query.all()

        for tax in taxes:
            self.api.upsert_tax(tax=tax)

        self.bridge_synchronize_entity.sw6_tax_sync_date = datetime.now()
        db.session.add(self.bridge_synchronize_entity)
        db.session.commit()

    def upsert_products(self):
        products = BridgeProductEntity.query.all()

        for product in products:
            self.api.upsert_product(product=product)

        self.bridge_synchronize_entity.sw6_product = datetime.now()
        db.session.add(self.bridge_synchronize_entity)
        db.session.commit()

    def sync_customers(self, erp_obj):

        # It is more likely that a new customer comes from the shop than from Bridge
        # So we check if the customers in sw6 are all in the bridge

        # Get all SW6 customer_addresses since the last sync date
        new_or_updated_customers = self.api.get_new_or_updated_customers()
        # Are new/updated customer available
        if new_or_updated_customers["total"] == 0:
            # No new customer we can return and do other stuff
            print("No New/Updated Customer in SW6 found")
            return True
        else:
            # Yes, we need some sync
            for new_customer in new_or_updated_customers["data"]:
                direction = self.upsert_or_downsert_customer(new_customer)
                print(direction)
                addresses_json = self.api.get_customer_addresses(new_customer["id"])
                addresses = addresses_json["data"]

                # bridge_customer_controller = Bridge2ObjectCustomerController(erp_obj=erp_obj)
                # bridge_customer_controller.upsert_from_sw6(customer=new_customer)
        return True

    def upsert_or_downsert_customer(self, sw6_customer):
        # Check if we need to upsert the customer or downsert it

        bridge_customer_entity = BridgeCustomerEntity()
        bridge_customer = bridge_customer_entity.query.filter_by(erp_nr=sw6_customer["customerNumber"]).one_or_none()
        if bridge_customer:
            print(sw6_customer["createdAt"], sw6_customer["updatedAt"])
            print(bridge_customer.created_at, bridge_customer.updated_at)

            sw6_customer_updated_at = parse_a_date_time(sw6_customer["updatedAt"], '%Y-%m-%dT%H:%M:%S.%f%z')
            # Direction Upsert from SW 6 -> Bridge
            if sw6_customer_updated_at >= bridge_customer.updated_at:
                return 'upsert'
            elif sw6_customer_updated_at < bridge_customer.updated_at:
                return 'downsert'
        else:
            # No Bridge_customer - so Upsert
            return 'upsert'

        return True

    def upsert_customer_address(self, customer_erp_nr):
        """
        Address are sync by the contact. Every address of a contact will bey synched. Informations are mixed between
        address and contact.
        :return:
        """
        return False  # ContactEntity

    def sync_orders(self):
        orders = self.api.get_orders()
        pprint(orders)

    def bulk_upload(self):
        categories = BridgeCategoryEntity().query.all()
        self.api.bulk_uploads(categories=categories)

