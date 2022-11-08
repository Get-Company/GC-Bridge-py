from typing import Any, Dict
from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaRelations
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from main.src.Controller.SW6.sw6_api_config import ConfShopware6ApiBase
from main.src.Entity.SW6.PayloadEntity import PayloadEntity

class SW6MediaInitEntity:
    def __init__(self, entity_type: str):
        self.__sw6_conf = ConfShopware6ApiBase()
        self.__sw6_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        self.__sw6_client = Shopware6AdminAPIClientBase(config=self.__sw6_conf)
        self.__type = entity_type
        self._sw6_entity = BridgeMediaRelations

    def init_entity(self):
        # columns = self._sw6_entity.query.statement.columns.keys()
        # print(columns)
        # medias = self._sw6_entity.query.all()
        # print(medias[0].product.name)
        try:
            rows = self._sw6_entity.query.all()
            for row in rows:
                payload = PayloadEntity(self.__type).setting_payload(row)
                # print(payload)
                try:
                    if payload:
                        uploaded_media_id = self.__insert_to_sw(payload)
                        row.media.sw6_uuid = uploaded_media_id
                        row.media.update_entity(row.media)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)


    def __insert_to_sw(self, payload: Dict[str, Any]):
        try:
            media = self.__sw6_client.request_post("media?_response=true")
            # print(media["data"]["id"])
            payload = {
                'url': payload['url']
            }
            extension = payload['url'].split('/')[-1].split('.')[-1]
            name = payload['url'].split('/')[-1].split('.')[0]
            # print(name)
            self.__sw6_client.request_post(f"_action/media/{media['data']['id']}/upload?extension={extension}&fileName={name}", payload)
            return media['data']['id']
        except Exception as e:
            print(e)
            return None