# from lib_shopware6_api_base import Shopware6AdminAPIClientBase, lib_shopware6_api_base_criteria as dal
from lib_shopware6_api import Shopware6AdminAPIClientBase, dal
from main.config import ConfShopware6ApiBase
from pprint import pprint

# Tools
import uuid
from main.src.Repository.functions_repository import get_current_datetime_and_convert_to_sw6_format

# Config
from main.config import ShopwareConfig as sw6config

# Bridge
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity


class SW6_2ObjectEntity:
    def __init__(self):
        print("SW6_2ObjectEntity Created")

        my_conf = ConfShopware6ApiBase
        my_api_client = Shopware6AdminAPIClientBase(config=my_conf)

        my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)

        self.api = my_api_client

    def delete_all_categories(self):
        categories = self.api.request_get(request_url='category')
        for cat in categories["data"]:
            if cat["id"] != "c9c5084cd0ed4e2da4a5db50234805f9":
                self.api.request_delete(f'category/'+str(cat["id"]))
            elif cat["id"] != "8de9b484c54f441c894774e5f57e485c":
                self.api.request_delete(f'category/' + str(cat["id"]))
            else:
                print("kuki")


        # self.api.request_delete('category/27aa4b00868a470cb4a346fe90a73dc0')


    def get_orders(self):
        payload = dal.Criteria()
        payload.associations['lineItems'] = dal.Criteria(limit=5)
        payload.associations['orderCustomer'] = dal.Criteria(limit=5)
        orders = self.api.request_post(request_url='search/order', payload=payload)
        pprint(orders)
        return orders

    def get_customers(self):
        customers = self.api.request_get(request_url='customer')
        return customers


    """
    SalesChannel
    """
    def get_saleschannel(self):
        sales_channels = self.api.request_get(request_url='sales-channel')
        for sc in sales_channels["data"]:
            if sc["name"] == 'Germany - Deutsch':
                pprint(sc)

    def create_saleschannel(self):
        payload = {
            {'_uniqueIdentifier': 'cd9a27ea46e840acbf0454e61737cdc4',
             'accessKey': sw6config.ACCESS_KEY,
             'active': sw6config.ACTIVE,
             'apiAlias': sw6config.APIALIAS,
             'countryId': sw6config.COUNTRY_DE,
             'createdAt': get_current_datetime_and_convert_to_sw6_format(),
             'currencies': sw6config.CURRENCY_EU,
             'currencyId': sw6config.CURRENCY_EU,
             'customerGroupId': sw6config.CUSTOMER_GROUP_DE_B2B,
             'homeEnabled': sw6config.HOME_ENABLED,
             # 'id': 'cd9a27ea46e840acbf0454e61737cdc4',
             'languageId': sw6config.LANGUAGE_ID_DE_DE,
             'navigationCategoryDepth': sw6config.NAVIGATION_CATEGORY_DEPTH,
             'navigationCategoryId': sw6config.NAVIGATION_CATEGORY_ID,
             'paymentMethodIds': [sw6config.PAYMENT_INVOICE_DE],
             'shippingMethodId': sw6config.SHIPPING_STANDARD,
             'typeId': uuid.uuid4().hex,
             }
        }

    """
    Customer
    """
    def find_customer(self, api_id):
        try:
            customer = self.api.request_get(request_url='customer/' + api_id)
            return customer
        except:
            return None

    def upsert_customer(self, adr_nr):
        customer_in_db = None
        try:
            customer_in_db = BridgeCustomerEntity().query.filter_by(erp_nr=adr_nr).one_or_none()
        except:
            print("Customer by AdrNr:", adr_nr, "not found in DB")

        if customer_in_db is not None:
            payload = {

            }





    """
    CustomerGroups
    """