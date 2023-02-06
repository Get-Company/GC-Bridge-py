from datetime import datetime

from main.src.SW6_Bridge.payloads import Payload


class CustomerPayload(Payload):
    def __init__(self, config):
        def create_payload(db_row):
            addresses_rows = [address for address in db_row.addresses]
            addresses_payload = []

            for address_row in addresses_rows:


                addresses_payload.append({
                    'id': address_row.api_id,
                    'firstName': address_row.na1,
                    'lastName': address_row.na2,
                    'email': address_row.email,
                    'street': address_row.str,
                    'zipcode': address_row.plz,
                    'city': address_row.city,
                    "countryId": self.config['sw_options']['customers_params']['countryId'],
                    "updatedAt": "2023-02-03T00:10:25.894+00:00",
                    "salutationId": "f1e1cbcb66b0426d8b947054e244ad0c"
                })

            payload = {
                "id": db_row.api_id,
                "customerNumber": db_row.erp_nr,
                "groupId": self.config['sw_options']['customers_params']['groupId'],
                "salesChannelId": self.config['sw_options']['customers_params']['salesChannelId'],
                "email": addresses_payload[0]['email'],
                "firstName": addresses_payload[0]['firstName'],
                "lastName": addresses_payload[0]['lastName'],
                "defaultPaymentMethodId": self.config['sw_options']['customers_params']['defaultPaymentMethodId'],
                "languageId": self.config['sw_options']['customers_params']['languageId'],
                "defaultBillingAddress": addresses_payload[0],
                "defaultShippingAddress": addresses_payload[0],
                "addresses": addresses_payload[1:] if len(addresses_payload) > 1 else None,
                "updatedAt": "2023-02-03T00:10:25.894+00:00",
                "salutationId": "f1e1cbcb66b0426d8b947054e244ad0c"
            }
            print(payload)
            return payload

        super().__init__(self, config, create_payload)










