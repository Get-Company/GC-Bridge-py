from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity


class SW5_2CustomerObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_customer(self, customer_id, is_number_not_id=False):
        url = f"/customers/{customer_id}"
        if is_number_not_id:
            url += '?useNumberAsId=true'
        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving customer with ID '{customer_id}': {e}")

    def get_customer_addresses(self, customer_id, is_number_not_id=False):
        url = f"/customers/{customer_id}/addresses"
        if is_number_not_id:
            url += '?useNumberAsId=true'
        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving customer with ID '{customer_id}': {e}")

    def get_all_customers_by_adrnr(self, adrnr):
        url = "/customers"
        url = url + f'?filter[number]={adrnr}'

        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving customers with same adrnr '{adrnr}': {e}")

    def get_all_customers_by_email(self, email):
        url = "/customers"
        url = url + f'?filter[email]={email}'

        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving customers with same email '{email}': {e}")

    """
    ### 
    Addresses
    ###
    """
    def get_all_addresses_by_customer(self, customer):
        customer_id = customer["id"]
        url = f"/customers/{customer_id}"
        filter = f"?filter[status]=0&filter[0][property]=orderTime&filter[0][expression]=>=&filter[0][value]={startdate}"
