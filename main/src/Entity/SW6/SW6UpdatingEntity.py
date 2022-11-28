from typing import Any, Dict
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from main.src.Controller.SW6.sw6_api_config import ConfShopware6ApiBase
from main.src.Entity.SW6.PayloadEntity import PayloadEntity

class SW6UpdatingEntity:
    def __init__(self, type: str, entity: any, last_update: any):
        self._sw6_conf = ConfShopware6ApiBase()
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self._sw6_conf)
        self.__type = type
        self.__sw6_entity = entity
        self.__last_update = last_update

    def sync_alle_geaenderte_die_mit_erp_ltz_nummer_in_db_gefunden_wurden_oder_auch_nicht_lade_in_sw_hoch(self):
        None


    def update_entity(self):
        try:
            columns = self.__sw6_entity.query.where(self.__sw6_entity.erp_ltz_aend > self.__last_update).statement.columns.keys()
            print(columns)
            rows = self.__sw6_entity.query.where(self.__sw6_entity.erp_ltz_aend > self.__last_update)
            for row in rows:
                payload = PayloadEntity(self.__type).setting_payload(row)
                # print(payload)
                if self.__is_exist_in_sw(payload): self.__update_to_sw(payload)
                else: self.__insert_to_sw(payload)

        except Exception as e:
            print(e)

    def __insert_to_sw(self, payload: Dict[str, Any]):
        try:
            print(f"/{self.__type}")
            self.__sw6_client.request_post(f"/{self.__type}", payload)
        except Exception as e:
            print(e)
            return None

    def __update_to_sw(self, payload: Dict[str, Any]):
        try:
            self.__sw6_client.request_patch(f"/{self.__type}/{payload['id']}", payload)
            print(payload['name'])
        except Exception as e:
            print(e)
            return None

    def __is_exist_in_sw(self, payload: Dict[str, Any]):
        result_dict = self.__sw6_client.request_get(f"/{self.__type}")
        all_id = []
        for elment in result_dict["data"]:
            all_id.append(elment["id"])
        if payload["id"] in all_id: return True
        else: return False

