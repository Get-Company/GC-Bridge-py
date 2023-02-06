import logging
from typing import Any, Dict
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
import requests

class Sw6Interface:
    def __init__(self, config, type: str):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self.__getSW6ApiConfigObj())
        self.__type = type

    def __getSW6ApiConfigObj(self):
        class ConfShopware6ApiBase(object):
            shopware_admin_api_url: str = self.config['sw_options_old']['shopware_admin_api_url']
            shopware_storefront_api_url: str = self.config['sw_options_old']['shopware_storefront_api_url']
            username: str = self.config['sw_options_old']['username']
            password: str = self.config['sw_options_old']['password']
            grant_type: str = self.config['sw_options_old']['grant_type']
        return ConfShopware6ApiBase()

    def initProcess(self):
        self.logger.info(f"The initialization started")
        self.logger.info(f"All initial task done")

    def updateProcess(self):
        self.logger.info(f"Updating")
        self.logger.info(f"Updating finished")

    def insert_to_sw(self, payload: Dict[str, Any]):
        self.logger.info(f"Try to insert data to Shopware")
        try:
            self.__sw6_client.request_post(f"/{self.__type}", payload)
            self.logger.info(f"Object inserted successfully - payload: {payload}")
        except Exception as e:
            self.logger.error(f"Failed to post to SW - error: {e}")
            return None

    def update_to_sw(self, payload: Dict[str, Any]):
        self.logger.info(f"Try to update data in Shopware")
        try:
            self.__sw6_client.request_patch(f"/{self.__type}/{payload['id']}", payload)
            self.logger.info(f"Object updated successfully - payload: {payload}")
        except Exception as e:
            self.logger.error(f"Failed to patch SW - error: {e}")
            return None

    def is_exist_in_sw(self, payload: Dict[str, Any]):
        result_dict = self.__sw6_client.request_get(f"/{self.__type}")
        all_id = []
        for elment in result_dict["data"]:
            all_id.append(elment["id"])
        if payload["id"] in all_id:
            return True
        else:
            return False

