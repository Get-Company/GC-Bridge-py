import logging
import time

from main.src.SW6_Bridge.config.config import config
from main.src.SW6_Bridge.methods.customer_methods import sync
from main.src.SW6_Bridge.modells import *
from main.src.SW6_Bridge.entity_service import CategoryService, CustomerService



class MainProcess:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config


    def sync_all_changed_customers_from_BRIDGE_to_SHOPWARE6(self):
        #db.Metadata.create_all(db.engine)
        sync.sync_all_changed_customers_from_BRIDGE_to_sw(config)

    def sync_all_changed_customers_from_SHOPWARE6_to_BRIDGE(self):
        sync.sync_all_changed_customers_from_SW_to_bridge(self.config)

    def upload_all_new_customer_from_SHOPWARE6_to_BRIDGE(self):
        sync.upload_all_new_customer_from_shopware_to_bridge(self.config)

    def sync_all_customer_from_BRIDGE_to_SHOPWARE6(self):
        CustomerService(self.config, db.session, Customer).init_model_for_sw()

    def sync_selected_customer_from_BRIDGE_to_SHOPWARE6(self, start, end):
        sync.sync_selected_customers_from_BRIDGE_to_sw_WITHOUT_SYNC_CHECK_NIIIIX_CHECKEN_DIESE(start, end)










#sync.sync_selected_customers_from_BRIDGE_to_sw_WITH_SYNC_CHECK(config, 10000, 15000)

            #atti_hilfe.sync_all_changed_customers_from_SW_to_bridge()

sw_bridge = MainProcess(config)