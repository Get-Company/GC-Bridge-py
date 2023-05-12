from main.src.Entity.SW5_2.APIClient import client_from_env
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPDigestAuth
from urllib3 import Retry


class SW5_2ObjectEntity():
    def __init__(self):

        self.base_url = "https://www.classei-shop.com/api"
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth('geco_bot', 'gpTCCXGurNt2JTnw0FDqXTLl0yMuh41hl18SVq3I')
        # Set up automatic retries on certain HTTP codes
        retry = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _make_request(self, method, url, payload=None):
        full_url = self.base_url + url
        try:
            response = self.session.request(method, full_url, json=payload)
            response.raise_for_status()
            json_response = response.json()
            if not json_response['success']:
                raise Exception('Shopware indicated a failure: %s' % json_response)
            return json_response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making {method} request to {full_url}: {e}")

    def get(self, url, data=None):
        try:
            return self._make_request('get', url, payload=data)
        except Exception as e:
            raise Exception(f"Error in GET request to {url}: {e}")

    def post(self, url, data):
        try:
            return self._make_request('post', url, payload=data)
        except Exception as e:
            raise Exception(f"Error in POST request to {url}: {e}")

    def put(self, url, data):
        try:
            return self._make_request('put', url, payload=data)
        except Exception as e:
            raise Exception(f"Error in PUT request to {url}: {e}")

    def delete(self, url, data=None):
        try:
            return self._make_request('delete', url, payload=data)
        except Exception as e:
            raise Exception(f"Error in DELETE request to {url}: {e}")


