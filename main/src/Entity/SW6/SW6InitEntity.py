from typing import Any, Dict
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from main.src.Controller.SW6.sw6_api_config import ConfShopware6ApiBase
from main.src.Entity.SW6.PayloadEntity import PayloadEntity

class SW6InitEntity:
    def __init__(self, entity_type: str):
        self.__sw6_conf = ConfShopware6ApiBase()
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self.__sw6_conf)
        self.__type = entity_type
        if entity_type == "category": self._sw6_entity = BridgeCategoryEntity
        elif entity_type == "category_with_parent": self._sw6_entity = BridgeCategoryEntity
        elif entity_type == "tax": self._sw6_entity = BridgeTaxEntity
        elif entity_type == "product": self._sw6_entity = BridgeProductEntity
        elif entity_type == "customer": self._sw6_entity = BridgeAdressenEntity
        else: print(f"Wrong type has been given: {entity_type}")

    def init_entity(self):
        # columns = self._sw6_entity.query.statement.columns.keys()
        # print(columns)
        # products = self._sw6_entity.query.all()
        # print(products[0].categories)
        try:
            rows = self._sw6_entity.query.all()
            for row in rows:
                payload = PayloadEntity(self.__type).setting_payload(row)
                print(payload)
                try:
                    # print(payload)
                    if payload:
                        if self.__type == "category_with_parent" and payload["parentId"] != "0": self.__update_to_sw(payload)
                        elif self.__type == "category_with_parent" and payload["parentId"] == "0": pass
                        else: self.__insert_to_sw(payload)
                    else: pass
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)


    def __insert_to_sw(self, payload: Dict[str, Any]):
        try:
            # print(f"/{self.__type}")
            self.__sw6_client.request_post(f"/{self.__type}", payload)
        except Exception as e:
            print(e)
            return None

    def __update_to_sw(self, payload: Dict[str, Any]):
        try:
            self.__sw6_client.request_patch(f"/{self.__type.split('_')[0]}/{payload['id']}", payload)
            #print(payload['name'])
        except Exception as e:
            print(e)
            return None