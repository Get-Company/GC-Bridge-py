from lib_shopware6_api import EqualsFilter
from typing import Any, Dict
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from main.src.Controller.SW6.sw6_api_config import ConfShopware6ApiBase
from main.src.Entity.SW6.PayloadEntity import PayloadEntity
from lib_shopware6_api_base import Criteria
import pprint

class Bridge2ObjectOrderController:
    def __init__(self):
        self.__sw6_conf = ConfShopware6ApiBase()
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self.__sw6_conf)


# SCHEISSE IST DES UM 23:30 :@@@@@@@@@@
    def get_orders(self):
        result_dict_order = self.__sw6_client.request_get("/order")
        order_ids = []
        for element in result_dict_order["data"]:
            element_dict = element["id"]
            #print(element_dict)
            o = element_dict
            order_ids.append(o)

        return order_ids

    def get_orders_product(self):
        order_dict = []
        order_ids = self.get_orders()
        for ids in order_ids:
            #print(ids)
            result_dict_order_products = self.__sw6_client.request_get(f"/order/{ids}/lineItems")
            #print(result_dict_order_products)

            for products in result_dict_order_products["data"]:
                #print(products)
                order_dict.append([products["orderId"], products["productId"]])
                #print(order_dict)
                #print(products["productId"])
            #     product_dicts = products["productId"]
            #     o = product_dicts
            #     order_product_ids.append(o)
        return order_dict







