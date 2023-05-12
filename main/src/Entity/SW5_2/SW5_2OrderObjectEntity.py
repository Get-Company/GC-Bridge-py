from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity
from datetime import datetime, date

class SW5_2OrderObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_order_by_id(self, id):
        """
        Retrieves an order by its ID.

        Args:
            id (int): The ID of the order.

        Returns:
            dict: The order data.

        Raises:
            Exception: If there is an error retrieving the order.
        """
        url = f'/orders/{id}'
        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving Order id {id}: {e}")


    def get_orders_by_customerId(self, customerId):
        """
        Retrieves orders for a specific customer.

        Args:
            customerId (int): The ID of the customer.

        Returns:
            list: A list of order data.

        """
        filter = '?filter[customerId]=%s' % customerId
        url = '/orders' + filter

        return self.get(url)['data']


    def get_todays_open_orders(self):
        """
        Retrieves today's open orders.

        Returns:
            list: A list of open order data.

        """
        return self.get_open_orders_by_startdate()


    def get_open_orders_by_startdate(self, startdate=None):
        """
        Retrieves open orders based on a specific start date.

        Args:
            startdate (str, optional): The start date to filter the orders. Defaults to today's date.

        Returns:
            list: A list of open order data.

        Raises:
            Exception: If there is an error retrieving the open orders.
        """
        if startdate is None:
            # Get today's date
            startdate = date.today().isoformat()

        filter = f"?filter[status]=0&filter[0][property]=orderTime&filter[0][expression]=>=&filter[0][value]={startdate}"
        url = '/orders' + filter

        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving open orders from {startdate}: {e}")


