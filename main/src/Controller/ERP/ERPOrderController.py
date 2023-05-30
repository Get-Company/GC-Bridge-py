from main.src.Controller.ERP.ERPController import ERPController
from main.src.Entity.ERP.ERPVorgangEntity import ERPVorgangEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity, BridgeOrderStateEntity, order_product
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity

from main import db
from pprint import pprint


class ERPOrderController(ERPController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj
        self.erp_entity = ERPVorgangEntity(erp_obj=erp_obj)
        self.bridge_entity = BridgeOrderEntity()
        self.last_sync_date = BridgeSynchronizeEntity().get_dataset_order_sync_date()

        self.new_orders = []

        super().__init__(erp_obj)

    def get_new_orders(self):
        """
        Query the database to get all orders with payment_state, shipping_state, and order_state equal to 0 (new orders).
        :return: A list of BridgeOrderEntity objects.
        """
        try:
            new_orders = BridgeOrderEntity.query.join(BridgeOrderStateEntity).filter(
                BridgeOrderStateEntity.payment_state == 0,
                BridgeOrderStateEntity.shipping_state == 0,
                BridgeOrderStateEntity.order_state == 0
            ).all()

            self.new_orders = new_orders
        except Exception as e:
            print(f"Error querying new orders: {str(e)}")

    def create_new_orders_in_erp(self):
        """
        Create new orders in ERP.

        Loops through the list of new orders and creates each order in the ERP system using the
        `create_new_order_in_erp` function. If the new_orders list is empty, the function will not execute.

        Returns:
            None
        """

        # Check if there are new orders to create in ERP
        if not self.new_orders:
            print("No new orders to create in ERP.")
            return

        print("Creating new orders in ERP...")

        # Loop through the new orders and create each order in ERP
        for order in self.new_orders:
            erp_order_id = self.create_new_order_in_erp(order)
            print(f"Order {erp_order_id} was created")
            order.order_state.order_state = 1
            order.erp_order_id = erp_order_id
            db.session.add(order)

        db.session.commit()
        db.session.close()
        print(f"{len(self.new_orders)} new orders created in ERP.")

    def create_new_order_in_erp(self, order):
        vorgang = ERPVorgangEntity(erp_obj=self.erp_obj)
        positions = self.get_all_data_from_order(order=order)
        erp_order_id = vorgang.create_new_webshop_order(order=order, positions=positions)

        if erp_order_id:
            pass

        return erp_order_id

    def get_all_data_from_order(self, order):
        print("Searching for position from order", order.id)
        order_id = order.id
        order = db.session.query(BridgeOrderEntity).filter(BridgeOrderEntity.id == order_id).first()
        if order:
            order_products = db.session.query(
                BridgeProductEntity,
                order_product.c.quantity,
                order_product.c.unit_price,
                order_product.c.total_price
            ).join(
                order_product,
                BridgeProductEntity.id == order_product.c.product_id
            ).filter(
                order_product.c.order_id == order.id
            ).all()
            result = {
                "order": order.__dict__,
                "order_products": []
            }
            for product, quantity, unit_price, total_price in order_products:
                product_dict = product.__dict__
                product_dict.pop("_sa_instance_state", None)
                product_dict["quantity"] = quantity
                product_dict["unit_price"] = unit_price
                product_dict["total_price"] = total_price
                result["order_products"].append(product_dict)
            return result
        else:
            print(f"No order found with id {order_id}")
            return False