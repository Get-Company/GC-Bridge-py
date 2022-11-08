from lib_shopware6_api import Shopware6AdminAPIClientBase, ConfShopware6ApiBase, dal
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import lru_cache
import pathlib
import inspect
from main.src.Repository.functions_repository import write_log


class SW6ObjectController:
    def __init__(self,
                 entity_name,
                 entity_instance,
                 entity_check_field,
                 class_name,
                 ):

        # if self.admin_client is None:
        #     self._admin_client = Shopware6AdminAPIClientBase(
        #         config=self.config,
        #         use_docker_test_container=self.use_docker_test_container)
        #     print("Admin Client Credentials were given")
        # else:
        #     self._admin_client = self.admin_client
        #     print("Admin Client Credentials weren't given")

        self._admin_client = Shopware6AdminAPIClientBase(
            use_docker_test_container=True
        )

        self.entity_check_field = entity_check_field
        self.entity_name = entity_name
        self.entity_instance = entity_instance
        self.class_name = class_name

    def upsert_ntt(self, ntt, add_parent=False):
        payload = self._map_db_to_sw6(ntt=ntt, add_parent=add_parent)
        id_in_db = self.is_already_in_sw6(check_value=ntt.api_id)
        if id_in_db:
            self._update_payload(id_in_db, payload=payload)
        else:
            self._insert_payload(api_id=ntt.api_id, payload=payload)

    def _map_db_to_sw6(self, ntt, add_parent=False):
        payload = self.entity_instance.map_db_to_sw6(ntt=ntt, add_parent=add_parent)
        return payload

    def _update_payload(self, id_in_db: str, payload: Dict[str, Any]) -> None:
        print("Update")
        print(f'{self.entity_check_field}')
        self._admin_client.request_patch(f"{self.entity_name}/{id_in_db}", payload)

    def _insert_payload(self, api_id: str, payload: Dict[str, Any]) -> None:
        print("Insert")
        payload["id"] = api_id
        self._admin_client.request_post(self.entity_name, payload)
        self.cache_clear()

    @lru_cache(maxsize=None)
    def is_already_in_sw6(self, check_value):
        print("Let's search for id %s in sw6." % check_value)

        payload = dal.Criteria()
        payload.page = 1
        payload.limit = 1
        payload.filter = [dal.EqualsFilter(field=self.entity_check_field, value=str(check_value))]
        payload.includes = {self.entity_name: ["id"]}

        dict_response = self._admin_client.request_post(request_url=f"search/{self.entity_name}", payload=payload)

        if dict_response['total'] >= 1:
            return_id = str(dict_response["data"][0]["id"])
            self.is_already_in_sw6.cache_clear()
        else:
            print(f'{self.entity_name} with id "{check_value}" not found')
            return_id = None

        return return_id

    # cache_clear_category{{{
    def cache_clear(self) -> None:
        """
        Cache of some functions has to be cleared if articles are inserted or deleted
        """
        # cache_clear_product}}}
        self.is_already_in_sw6.cache_clear()

    def db_save_all_to_sw6(self):
        pass

    def upsert_images_to_sw6(self, ntt):
        pass

    def print_method_info(self, name):
        print('\n#- %s %s -#' % (name, inspect.currentframe().f_back.f_code.co_name))
        write_log('#- %s %s -#' % (name, inspect.currentframe().f_back.f_code.co_name))
