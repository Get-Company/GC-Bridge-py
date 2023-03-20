from typing import Any, Dict
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from main.src.Controller.SW6.sw6_api_config import ConfShopware6ApiBase
import itertools

class Bridge2ObjectOrderController:
    def __init__(self):
        self.__sw6_conf = ConfShopware6ApiBase()
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self.__sw6_conf)



    def get_orders(self):
        """
                Get all orderID ( API ID ) from Shopware via API
                self.__sw6_client.request_get("/order")
                output example for 3 orders:

                ['34c6880c901940c0b8bb095f4ba8bf6e',
                 '4ec69c9030534c7bbcc3837e835f5ad6',
                 '7a771bf222394a7fa9b9ad3d08b38d6c']

        """
        result_dict_order = self.__sw6_client.request_get("/order")
        order_ids = []
        for element in result_dict_order["data"]:
            element_dict = element["id"]
            o = element_dict
            order_ids.append(o)

        return order_ids

    def get_orders_product(self):
        """
                #### Many(Products) to one(Orders) Relation ###

                Give all orderID ( API ID ) to Shopware request:
                self.__sw6_client.request_get(f"/order/{ids}/lineItems")
                lineItems = Product info from Shopware
                output example for 3 orders:

                [['34c6880c901940c0b8bb095f4ba8bf6e', 'b0990364a1da4893a2042f39a779101d'],
                 ['4ec69c9030534c7bbcc3837e835f5ad6', '5be09cc2baf148d19fe6629535629395'],
                 ['7a771bf222394a7fa9b9ad3d08b38d6c', 'b0990364a1da4893a2042f39a779101d'],
                 ['7a771bf222394a7fa9b9ad3d08b38d6c', '3ac014f329884b57a2cce5a29f34779c'],
                 ['7a771bf222394a7fa9b9ad3d08b38d6c', '1807e31cf08c44c09e2313352ad93e3a'],
                 ['7a771bf222394a7fa9b9ad3d08b38d6c', '5be09cc2baf148d19fe6629535629395']]

                 Where for example "5be09cc2baf148d19fe6629535629395" is ProductID from Shopware

        """
        order_product = []
        order_ids = self.get_orders()
        for ids in order_ids:
            result_dict_order_products = self.__sw6_client.request_get(f"/order/{ids}/lineItems")

            for products in result_dict_order_products["data"]:
                order_product.append([products["orderId"], products["productId"]])
        return order_product

    def get_orders_customer(self):
        """
                #### One(Customer) to Many(Orders) Relation ###

                Give all orderID ( API ID ) to Shopware request:
                self.__sw6_client.request_get(f"/order/{ids}/orderCustomer")
                orderCustomer = Customer info from Shopware
                output example for 3 orders:

                [['34c6880c901940c0b8bb095f4ba8bf6e', 'a5937fc5e33e4fef833e4aa11ede7aa5'],
                 ['4ec69c9030534c7bbcc3837e835f5ad6', 'a5937fc5e33e4fef833e4aa11ede7aa5'],
                 ['7a771bf222394a7fa9b9ad3d08b38d6c', 'a5937fc5e33e4fef833e4aa11ede7aa5']]

                 Where for example "a5937fc5e33e4fef833e4aa11ede7aa5" is CustomerID from Shopware

                """
        order_customer = []
        order_ids = self.get_orders()
        for ids in order_ids:
            result_dict_order_products = self.__sw6_client.request_get(f"/order/{ids}/orderCustomer")

            for products in result_dict_order_products["data"]:
                order_customer.append([products["orderId"], products["customerId"]])
        return order_customer

    def make_order_list(self):

        """
                        Make a simple one layer list
                        from Product_order or Customer_order

                        !!!is optional, not main funktion!!!

                        """

        result_list = []
        prodcut = self.get_orders_product()
        for order_id in prodcut:
            for order_id_2 in order_id:
                result_list.append(order_id_2)
                print(order_id_2)

        return result_list

    def make_order_dict_products(self):

        """
                        Make a dict with multiple values
                        with relation to orders and products.

                        Example:

                        {'34c6880c901940c0b8bb095f4ba8bf6e': ['b0990364a1da4893a2042f39a779101d'],
                        '4ec69c9030534c7bbcc3837e835f5ad6': ['5be09cc2baf148d19fe6629535629395'],
                        '7a771bf222394a7fa9b9ad3d08b38d6c': ['b0990364a1da4893a2042f39a779101d',
                                                              '3ac014f329884b57a2cce5a29f34779c',
                                                              '1807e31cf08c44c09e2313352ad93e3a',
                                                              '5be09cc2baf148d19fe6629535629395']}

                        Where for example "34c6880c901940c0b8bb095f4ba8bf6e" is OrderID
                        and for example "b0990364a1da4893a2042f39a779101d" is ProductID


                        Key = Order ID
                        Value = (list)[Product ID1, ProductID2......]

                        """


        s = self.get_orders_product()
        output_products = {}
        for k, *v in s:
            if v:
                output_products.setdefault(k, []).extend(v)
            else:
                output_products[k] = None
        return output_products

    def make_order_dict_customers(self):

        """
                        Make a dict with multiple values
                        with relation to orders and customers. Example:

                        {'34c6880c901940c0b8bb095f4ba8bf6e': ['a5937fc5e33e4fef833e4aa11ede7aa5'],
                         '4ec69c9030534c7bbcc3837e835f5ad6': ['a5937fc5e33e4fef833e4aa11ede7aa5'],
                         '7a771bf222394a7fa9b9ad3d08b38d6c': ['a5937fc5e33e4fef833e4aa11ede7aa5']}

                        Where for example "34c6880c901940c0b8bb095f4ba8bf6e" is OrderID
                        and for example "a5937fc5e33e4fef833e4aa11ede7aa5" is CustomerID

                        Key = Order ID
                        Value = (list)[Customer ID]

                        """

        s = self.get_orders_customer()
        output_customers = {}
        for k, *v in s:
            if v:
                output_customers.setdefault(k, []).extend(v) #Control the key-value pairs
            else:
                output_customers[k] = None
        return output_customers

    def order_products_relation(self, orderid=str):

        """
                        Make a simple one layer list
                        with relation to orders and products. Example:

                        ['b0990364a1da4893a2042f39a779101d',
                         '3ac014f329884b57a2cce5a29f34779c',
                         '1807e31cf08c44c09e2313352ad93e3a',
                         '5be09cc2baf148d19fe6629535629395']

                        Where parameter(orderid) is OrderID
                        and for example "b0990364a1da4893a2042f39a779101d" is ProductID



                        """

        list = self.make_order_dict_products()
        result_list_p = list[orderid]
        return result_list_p

    def order_customer_relation(self, orderid=str):

        """
                        Make a simple one layer list
                        with relation to orders and customers. Example:

                        ['a5937fc5e33e4fef833e4aa11ede7aa5']

                        Where parameter(orderid) is OrderID
                        and for example "a5937fc5e33e4fef833e4aa11ede7aa5" is CustomerID



                        """

        list = self.make_order_dict_customers()
        result_list_c = list[orderid]
        return result_list_c









