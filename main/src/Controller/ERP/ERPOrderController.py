from loguru import logger
from sqlalchemy import or_

from main.src.Controller.ERP.ERPController import ERPController
from main.src.Entity.ERP.ERPVorgangEntity import ERPVorgangEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import (
    BridgeOrderEntity,
    BridgeOrderStateEntity,
    order_product
)
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main import db

class ERPOrderController(ERPController):
    def __init__(self, erp_obj):
        super().__init__(erp_obj)
        self.erp_obj = erp_obj
        self.erp_entity = ERPVorgangEntity(erp_obj=erp_obj)
        self.bridge_entity = BridgeOrderEntity()
        self.last_sync_date = BridgeSynchronizeEntity().get_dataset_order_sync_date()
        self.new_orders = []
        logger.info("ERPOrderController initialized, last_sync_date=%s", self.last_sync_date)

    def get_new_orders(self):
        """
        Query the database for orders with payment_state, shipping_state, and order_state == 0.
        """
        try:
            self.new_orders = (
                BridgeOrderEntity.query
                .join(BridgeOrderStateEntity)
                .filter(
                    or_(
                        BridgeOrderStateEntity.payment_state.in_([0, 17]),
                    ),
                    BridgeOrderStateEntity.shipping_state == 0,
                    BridgeOrderStateEntity.order_state == 0
                )
                .all()
            )
            logger.info("Fetched %d new orders", len(self.new_orders))
        except Exception as e:
            logger.error("Error querying new orders: {}", e)
            self.new_orders = []

    def create_new_orders_in_erp(self):
        """
        Loops through new_orders and creates each in the ERP system.
        """
        if not self.new_orders:
            logger.info("No new orders to create in ERP.")
            return

        logger.info("Creating %d new orders in ERP...", len(self.new_orders))
        for order in self.new_orders:
            erp_order_id = self.create_new_order_in_erp(order)
            if erp_order_id:
                order.order_state.order_state = 1
                order.erp_order_id = erp_order_id
                db.session.add(order)
                logger.info("Order %s created in ERP with ID %s", order.id, erp_order_id)
            else:
                logger.warning("Failed to create order %s in ERP", order.id)

        try:
            db.session.commit()
            logger.info("Committed %d orders to database", len(self.new_orders))
        except Exception as e:
            logger.error("Error committing new orders: {}", e)
        finally:
            db.session.close()

    def create_new_order_in_erp(self, order):
        """
        Create a single order in ERP and return the ERP order ID.
        """
        positions = self.get_all_data_from_order(order)
        try:
            erp_order_id = self.erp_entity.create_new_webshop_order(
                order=order,
                positions=positions
            )
            return erp_order_id
        except Exception as e:
            logger.error("Error creating order %s in ERP: {}", order.id, e)
            return None

    def get_all_data_from_order(self, order):
        """
        Retrieves all line items for a given order from the Bridge database.
        """
        logger.info("Retrieving positions for order %s", order.id)
        try:
            order_in_db = (
                db.session.query(BridgeOrderEntity)
                .filter_by(id=order.id)
                .first()
            )
            if not order_in_db:
                logger.warning("Order %s not found in DB", order.id)
                return []

            order_products = (
                db.session.query(
                    BridgeProductEntity,
                    order_product.c.quantity,
                    order_product.c.unit_price,
                    order_product.c.total_price
                )
                .join(
                    order_product,
                    BridgeProductEntity.id == order_product.c.product_id
                )
                .filter(order_product.c.order_id == order.id)
                .all()
            )

            result = {
                "order": {k: v for k, v in order_in_db.__dict__.items() if not k.startswith('_sa_')},
                "order_products": []
            }
            for product, quantity, unit_price, total_price in order_products:
                pdict = {k: v for k, v in product.__dict__.items() if not k.startswith('_sa_')}
                pdict.update({
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                })
                result["order_products"].append(pdict)

            logger.info("Retrieved %d positions for order %s", len(result["order_products"]), order.id)
            return result
        except Exception as e:
            logger.error("Error fetching positions for order %s: {}", order.id, e)
            return []
