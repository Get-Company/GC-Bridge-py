from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from main.src.Controller.SW6.sw6_api_config import ConfShopware6ApiBase
import itertools

class SW6CustomerController:
    def __init__(self):
        self.__sw6_conf = ConfShopware6ApiBase()
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self.__sw6_conf)



    def get_customers(self):
        """
                Get all orderID ( API ID ) from Shopware via API
                self.__sw6_client.request_get("/order")
                output example for 3 orders:

                ['34c6880c901940c0b8bb095f4ba8bf6e',
                 '4ec69c9030534c7bbcc3837e835f5ad6',
                 '7a771bf222394a7fa9b9ad3d08b38d6c']

        """
        result_dict_order = self.__sw6_client.request_get("/customer_address")
        customers = []
        for element in result_dict_order["data"]:
            customers.append(element)

        return customers
