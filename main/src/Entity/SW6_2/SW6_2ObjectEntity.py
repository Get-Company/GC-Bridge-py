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