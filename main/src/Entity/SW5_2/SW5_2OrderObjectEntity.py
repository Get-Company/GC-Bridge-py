from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity
from datetime import datetime, date, timedelta

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
            return response
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

        filter = f"?filter[0][property]=status" \
                 f"&filter[0][value]=0" \
                 f"&filter[1][property]=orderTime" \
                 f"&filter[1][expression]=>=" \
                 f"&filter[1][value]={startdate}"
        url = '/orders' + filter

        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving open orders from {startdate}: {e}")

    def get_open_orders_by_startdate_and_enddate(self, startdate=None, enddate=None):
        """
        Retrieves open orders based on a specific start date.

        Args:
            startdate (str, optional): The start date to filter the orders. Defaults to today's date.
            enddate (str, optional): The end date to filter the orders. Defaults to today's date + 1 day.

        Returns:
            list: A list of open order data.

        Raises:
            Exception: If there is an error retrieving the open orders.
        """
        if startdate is None:
            # Get today's date
            startdate = date.today().isoformat()

        if enddate is None:
            # Get tomorrow's date
            enddate = (date.today() + timedelta(days=1)).isoformat()

        filter = f"?filter[0][property]=status" \
                 f"&filter[0][value]=0" \
                 f"&filter[1][property]=orderTime" \
                 f"&filter[1][expression]=>=" \
                 f"&filter[1][value]={startdate}" \
                 f"&filter[2][property]=orderTime" \
                 f"&filter[2][expression]=<" \
                 f"&filter[2][value]={enddate}"

        url = '/orders' + filter

        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving open orders from {startdate} to {enddate}: {e}")

    def set_order_and_payment_status(self, order_id, payment_status_id, order_status_id):
        url = '/orders/%s' % order_id
        print(f"Try updating order {order_id} with payment status: {payment_status_id} and order status: {order_status_id}")
        data = {
            'paymentStatusId': payment_status_id,
            'orderStatusId': order_status_id
        }
        try:
            response = self.put('/orders/%s' % order_id, data)['data']
            return response
        except Exception as e:
            raise Exception(f"Error on updating Order- and Payment-Status for OrderId: {order_id}: {e}")

