from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import requests
import logging
from datetime import datetime, timedelta
from config import config
from modells.Customer import Customer, CustomerAddress
from pprint import pprint


config = config
sw6_client_admin_url = config['sw_options']['shopware_admin_api_url']
sw6_client_auth_url = config['sw_options']['shopware_auth_url']
sw6_client_auth_params = {
    'grant_type': config['sw_options']['grant_type'],
    'client_id': config['sw_options']['client_id'],
    'client_secret': config['sw_options']['client_secret']
}
resp = requests.post(sw6_client_auth_url, data=sw6_client_auth_params).json()
access_token = resp['access_token'] if 'access_token' in resp.keys() else None
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}
db_row
engine = create_engine("mysql+pymysql://root:@localhost:3306/shopware")
Session = sessionmaker(bind=engine)
session = Session()


addresses_rows = [address for address in db_row.addresses]
addresses_payload = []

for address_row in addresses_rows:


    addresses_payload.append({
        # "customerId": db_row.api_id,
        'id': address_row.api_id,
        'firstName': address_row.na1,
        'lastName': address_row.na2,
        'email': address_row.email,
        'street': address_row.str,
        'zipcode': address_row.plz,
        'city': address_row.city,
        "countryId": config['sw_options']['customers_params']['countryId']
    })
    #rint(addresses_payload)
# print(json.dumps(addresses_payload, indent=4))
payload = {
    "id": db_row.api_id,
    "customerNumber": db_row.api_id,
    "groupId": config['sw_options']['customers_params']['groupId'],
    "salesChannelId": config['sw_options']['customers_params']['salesChannelId'],
    "email": addresses_payload[0]['email'],
    "firstName": addresses_payload[0]['firstName'],
    "lastName": addresses_payload[0]['lastName'],
    "defaultPaymentMethodId": config['sw_options']['customers_params']['defaultPaymentMethodId'],
    "languageId": config['sw_options']['customers_params']['languageId'],
    "defaultBillingAddress": addresses_payload[0],
    # "defaultShippingAddress": addresses_payload[0],
    "addresses": addresses_payload[1:] if len(addresses_payload) > 1 else None
}
print(payload)
