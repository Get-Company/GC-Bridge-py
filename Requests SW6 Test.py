import requests
import json



sw6_client_admin_url = "http://localhost/api"
sw6_client_auth_url = "http://localhost/api/oauth/token"


sw6_client_auth_params = {
    'grant_type': "client_credentials",
    'client_id': "SWIASGDMB2R4ETRVCEP3Q3DSEA",
    'client_secret': "aGd5RW1NZE1rSW5ZeXBjdHRqOVAyQUpTaTBxamFuVmlSRXBjUW0"
}


resp = requests.post(sw6_client_auth_url, data=sw6_client_auth_params).json()

access_token = resp['access_token'] if 'access_token' in resp.keys() else None


headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}


url = sw6_client_admin_url + '/customer'
response = requests.get(url, headers=headers)
from pprint import pprint


data = response.json()

pprint(data)