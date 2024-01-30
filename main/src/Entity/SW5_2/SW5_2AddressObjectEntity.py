from pprint import pprint

from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity


class SW5_2AddressObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_address(self, address_id):
        url = f"/addresses/{address_id}"
        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving address with ID '{address_id}': {e}")

    def update(self, address):
        data = address
        try:
            response = self.put('/addresses/%s' % address['data']['id'], data)['data']
            return response
        except Exception as e:
            pprint(e)
            raise Exception(f"Error on updating Address: {address['data']['id']} on Address_ID: {address['data']['id']}: {e}")
