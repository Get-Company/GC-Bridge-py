import json
import requests
import logging
from datetime import datetime, timedelta
from pprint import pprint
class Sw6Interface:
    def __init__(self, config, type):
        self.logger = logging.getLogger(__name__)
        self.__type = type
        self.config = config
        self.__sw6_client_admin_url = self.config['sw_options']['shopware_admin_api_url']
        self.__sw6_client_auth_url = self.config['sw_options']['shopware_auth_url']
        self.__sw6_client_auth_params = {
            'grant_type': self.config['sw_options']['grant_type'],
            'client_id': self.config['sw_options']['client_id'],
            'client_secret': self.config['sw_options']['client_secret']
        }
        self.access_token = None
        self.access_token_expiration = datetime.now()

    def __get_access_token(self):
        self.logger.info("Sw6Interface - __get_access_token - Try to get new access token for client")
        try:
            resp = requests.post(self.__sw6_client_auth_url, data=self.__sw6_client_auth_params).json()
            self.access_token = resp['access_token'] if 'access_token' in resp.keys() else None
            self.access_token_expiration = (datetime.now() + timedelta(seconds=resp['expires_in'])) if 'expires_in' in resp.keys() else None
            self.logger.info(f"Sw6Interface - __get_access_token - Token has been taken successfully - it is valid until {resp['expires_in']} sec") if self.access_token != None else self.logger.error(f"Sw6Interface - __get_access_token - Problem occured during getting access token - {resp}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Sw6Interface - __get_access_token - Problem occured during getting access token - error: {e}")
            raise SystemExit(e)


    def sync_entity_to_sw(self, payloads):
        self.logger.info(f"Sw6Interface - sync_entity_to_sw - Try to init and upload all {self.__type} data")
        if self.access_token_expiration <= datetime.now():
            self.logger.info(f"Sw6Interface - sync_entity_to_sw - Access token has expired")
            self.__get_access_token()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        data = json.dumps([
            {
                "action": "upsert",
                "entity": f"{self.__type}",
                "payload": payloads
            }
        ], indent=4)
        try:
            response = requests.post(f"{self.__sw6_client_admin_url}/_action/sync", headers=headers, data=data).json()
            self.logger.info(f"Sw6Interface - sync_entity_to_sw - Uploading finished successfully - {len(response['data'][0]['result'])} {self.__type} data uploaded")  \
                if ((response['success'] == True) if 'success' in response.keys() else None) \
                else self.logger.error(f"Sw6Interface - sync_entity_to_sw - Problem occurred during uploading - {response['errors'] if 'errors' in response.keys() else response['data'][0]['result'][0]}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Sw6Interface - sync_entity_to_sw - Failed to init all {self.__type} for SW - error: {e}")
            raise SystemExit(e)
