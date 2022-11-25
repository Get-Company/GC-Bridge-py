# from lib_shopware6_api_base import Shopware6AdminAPIClientBase, lib_shopware6_api_base_criteria as dal
from lib_shopware6_api import Shopware6AdminAPIClientBase, dal
from main.config import ConfShopware6ApiBase
from pprint import pprint


class SW6_2ObjectEntity:
    def __init__(self):
        print("SW6_2ObjectEntity Created")

        my_conf = ConfShopware6ApiBase
        my_api_client = Shopware6AdminAPIClientBase(config=my_conf)

        my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)

        self.api = my_api_client

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
