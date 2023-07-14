import math

from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity
from datetime import datetime, date, timedelta

class SW5_2ProductObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_product_by_id(self, id):
        """
        Retrieves an order by its ID.

        Args:
            id (int): The ID of the order.

        Returns:
            dict: The order data.

        Raises:
            Exception: If there is an error retrieving the order.
        """
        url = f'/articles/{id}'
        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving Product id {id}: {e}")

    def set_special_price_by_bridge_product_object(self, bridge_product):
        url = f'/articles/{bridge_product.erp_nr}?useNumberAsId=true'
        customer_groups = {'CHB2C': 1.3, 'CHB2B': 1.3, 'IT_de': 1.26, 'IT_it': 1.26, 'Vk0': 1, 'Vk1': 1, 'EK': 1}

        prices = []
        for customer_group_key, factor in customer_groups.items():
            if factor is 1:
                price = bridge_product.prices.price
                special_price = bridge_product.prices.special_price
            else:
                price = math.ceil((bridge_product.prices.price * factor) / 0.05) * 0.05
                special_price = math.ceil((bridge_product.prices.special_price * factor) / 0.05) * 0.05

            price_data = {
                "customerGroupKey": customer_group_key,
                "from": 1,
                "to": "beliebig",
                "price": special_price,
                "pseudoPrice": price
            }
            prices.append(price_data)

        data = {
            "mainDetail": {
                "prices": prices
            }

        }
        try:
            response = self.put(url, data)['data']
            return response
        except Exception as e:
            raise Exception(f"Error on updating special prices for {bridge_product.erp_nr}: {e}")

    def set_price_by_bridge_product_object(self, bridge_product):
        url = f'/articles/{bridge_product.erp_nr}?useNumberAsId=true'
        customer_groups = {'CHB2C': 1.3, 'CHB2B': 1.3, 'IT_de': 1.26, 'IT_it': 1.26, 'Vk0': 1, 'Vk1': 1, 'EK': 1}

        prices = []
        for customer_group_key, factor in customer_groups.items():
            price = math.ceil((bridge_product.prices.price * factor) / 0.05) * 0.05
            special_price = None
            price_data = {
                "customerGroupKey": customer_group_key,
                "from": 1,
                "to": "beliebig",
                "price": price,
                "pseudoPrice": special_price
            }
            prices.append(price_data)

        data = {
            "mainDetail": {
                "prices": prices
            }

        }
        try:
            response = self.put(url, data)['data']
            return response
        except Exception as e:
            raise Exception(f"Error on updating prices for {bridge_product.erp_nr}: {e}")

