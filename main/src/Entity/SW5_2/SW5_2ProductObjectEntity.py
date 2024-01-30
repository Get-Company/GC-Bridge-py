import math
from pprint import pprint

from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity
from main.src.Entity.SW5_2.SW5_2CategoryObjectEntity import SW5_2CategoryObjectEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from datetime import datetime, date, timedelta


class SW5_2ProductObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        # It 06.12.23: 1.26 -> 1.0413
        self.factor_it = 1.0413
        # CH 01.03.21: 1.4 -> 1.35
        # CH 01.03.22: 1.35 -> 1.3
        self.factor_ch = 1.3

        self.customer_groups = {
            'CHB2C': self.factor_ch, 'CHB2B': self.factor_ch,
            'IT_de': self.factor_it, 'IT_it': self.factor_it,
            'Vk0': 1, 'Vk1': 1, 'EK': 1
        }

        super().__init__()

    def map_bridge_to_sw5(self, entity):
        data = {
            "active": True,
            # "added": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "description": entity.description_short,
            "descriptionLong": entity.description,
            "tax": entity.tax.satz,
            "supplier": "Classei",
            "mainDetail": {
                "number": entity.erp_nr,
                "inStock": entity.stock,
                "maxPurchase": self.get_max_purchase(entity=entity),
                "minPurchase": entity.min_purchase,
                "packUnit": "Stck" if "% Stck" in entity.unit else entity.unit,
                "purchaseSteps": entity.purchase_unit,
                "attr1": None,
                "attr2": None,
                "attr3": None,
                "attr4": None,
                "attr5": None,
                "attr6": None,
                "attr7": None,
                "attr8": None,
                "attr9": None,
                "attr10": None,
                "attr11": None,
                "attr12": None,
                "attr13": None,
                "attr14": None,
                "attr15": None,
                "attr16": None,
                "attr17": None,
                # "attr18": Sortierung
                # "attr19": Fixe Versandkosten
                # "attr20": Pro St. 1x fixe Versandkosten
                "gcFaktor": entity.factor if entity.factor != 0 else None,
            },
            "metaTitle": entity.name,
            "name": entity.name,
        }
        return data

    def get_stock(self, entity):
        entries = int((entity.stock - entity.min_purchase) / entity.purchase_unit)
        if entries > 1000:
            return 1000 * entity.purchase_unit
        else:
            return entity.stock

    def get_max_purchase(self, entity):
        max_purchase = 2000 * entity.purchase_unit
        return max_purchase

    def get_product_by_id(self, id, use_order_number=False):
        """
        Retrieves an order by its ID.

        Args:
            id (int): The ID of the order.
            or
            ordernerumber example: 581000

        Returns:
            dict: The order data.

        Raises:
            Exception: If there is an error retrieving the order.
        """
        url = f'/articles/{id}'
        if use_order_number:
            url += '?useNumberAsId=true'
        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving Product id {id}: {e}")

    def set_special_price_by_bridge_product_object(self, bridge_product):
        url = f'/articles/{bridge_product.erp_nr}?useNumberAsId=true'

        prices = []
        for customer_group_key, factor in self.customer_groups.items():
            if factor == 1:
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

        prices = []
        for customer_group_key, factor in self.customer_groups.items():
            price = math.ceil((bridge_product.prices.price * factor) / 0.05) * 0.05
            rebate_price = math.ceil((bridge_product.prices.rebate_price * factor) / 0.05) * 0.05

            # Staffelpreise
            if bridge_product.prices.rebate_quantity and bridge_product.prices.rebate_price:
                price_data = {
                    "customerGroupKey": customer_group_key,
                    "from": 1,
                    "to": bridge_product.prices.rebate_quantity - 1,
                    "price": price,
                    "pseudoPrice": None
                }
                prices.append(price_data)
                rebate_price_data = {
                    "customerGroupKey": customer_group_key,
                    "from": bridge_product.prices.rebate_quantity,
                    "to": "beliebig",
                    "price": rebate_price,
                    "pseudoPrice": None
                }
                prices.append(rebate_price_data)
            else:
                price_data = {
                    "customerGroupKey": customer_group_key,
                    "from": 1,
                    "to": "beliebig",
                    "price": price,
                    "pseudoPrice": None
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

    def set_price_data(self, bridge_product):
        url = f'/articles/{bridge_product.erp_nr}?useNumberAsId=true'
        customer_groups = {'CHB2C': 1.3, 'CHB2B': 1.3, 'IT_de': 1.26, 'IT_it': 1.26, 'Vk0': 1, 'Vk1': 1, 'EK': 1}

        prices = []

        for customer_group_key, factor in customer_groups.items():
            price = math.ceil((bridge_product.prices.price * factor) / 0.05) * 0.05
            special_price = bridge_product.prices.special_price
            if special_price:
                special_price = math.ceil((special_price * factor) / 0.05) * 0.05
            rebate_price = math.ceil((bridge_product.prices.rebate_price * factor) / 0.05) * 0.05

            # If special price dates are set and valid
            if (bridge_product.prices.special_start_date and bridge_product.prices.special_end_date and
                    bridge_product.prices.special_start_date <= datetime.now() <= bridge_product.prices.special_end_date):
                price_data = {
                    "customerGroupKey": customer_group_key,
                    "from": 1,
                    "to": "beliebig",
                    "price": special_price,
                    "pseudoPrice": price
                }
            else:
                special_price = None  # Set special_price to None if dates don't apply
                price_data = {
                    "customerGroupKey": customer_group_key,
                    "from": 1,
                    "to": "beliebig",
                    "price": price,
                    "pseudoPrice": special_price
                }

            prices.append(price_data)

            # Regular price and rebate price
            if bridge_product.prices.rebate_quantity and bridge_product.prices.rebate_price:
                rebate_price_data = {
                    "customerGroupKey": customer_group_key,
                    "from": bridge_product.prices.rebate_quantity,
                    "to": "beliebig",
                    "price": rebate_price,
                    "pseudoPrice": None
                }
                prices.append(rebate_price_data)

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

    def update(self, bridge_product_id=None, bridge_entity=None):
        if not bridge_product_id and not bridge_entity:
            print("At least set one value: bridge_product_id oder bridge_entity")
            return False
        try:
            if bridge_entity:
                product = bridge_entity
            else:
                product = BridgeProductEntity.query.get(bridge_product_id)
        except Exception as e:
            print(f"Couldn't find product by product.id:", bridge_product_id, e)
            return False

        if product.wwshopkz != 1:
            print(f"No update for {product.erp_nr}. WShopKz is: {product.wshopkz}. Leaving update method")
            return

        try:
            sw5_product = self.get_product_by_id(product.erp_nr, True)
        except Exception as e:
            print(f"Couldn't find {product.erp_nr} in SW5")
            return False

        url = f'/articles/{sw5_product["data"]["id"]}'
        data = self.map_bridge_to_sw5(product)
        try:
            response = self.put(url, data)["data"]
            return response
        except Exception as e:
            print(f'Couldn\'t update {product.erp_nr} with id:{sw5_product["data"]["id"]}')

    def create_product(self, product_id):
        try:
            product = BridgeProductEntity.query.get(product_id)
            if product.wwshopkz != 1:
                print(f"Ca not create {product.erp_nr}. WShopKz is: {product.wshopkz}. Leaving method")
                return
        except Exception as e:
            print(f"Couldn't find product by product.id:", product_id, e)
            return False

        url = f'/articles'
        data = self.map_bridge_to_sw5(product)
        try:
            response = self.post(url, data)['data']
            return response
        except Exception as e:
            print(f"Could not create {product.name}:", e)





