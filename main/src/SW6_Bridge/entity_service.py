from main.src.SW6_Bridge.payloads import *
from main.src.SW6_Bridge.sw6_interface import Sw6Interface
import logging
import json

class EntityService:
    def __init__(self, config, db_session, model, init_callback):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.db_session = db_session
        self.model = model
        self.columns = self.db_session.query(self.model).statement.columns.keys()
        self.init_callback = init_callback

    def init_model_for_sw(self):
        rows = self.db_session.query(self.model).all()
        self.init_callback(rows)

class CategoryService(EntityService):
    def __init__(self, config, db_session, model):
        def __category_init(rows):
            self.logger.info("CategoryService - __category_init - Initializing categories")
            payloads = CategoryPayload(config).get_payload(rows)
            payloads_without_parent = [{key: value for key, value in payload.items() if key != 'parentId'} for payload in payloads]
            payloads_with_parent = [payload for payload in payloads if payload['parentId'] != '0']
            sw6 = Sw6Interface(config, 'category')
            self.logger.info("CategoryService - __category_init - Uploading categories without parend id parameter")
            sw6.sync_entity_to_sw(payloads_without_parent)
            self.logger.info("CategoryService - __category_init - Uploading categories with parend id parameter to organize them hierarchically")
            sw6.sync_entity_to_sw(payloads_with_parent)



        self.__init_callback = lambda rows: __category_init(rows)
        super().__init__(config, db_session, model, self.__init_callback)



class CustomerService(EntityService):
    def __init__(self, config, db_session, model):
        def __category_init(rows):
            self.logger.info("CustomerService - __category_init - Initializing customers")
            payloads = CustomerPayload(config).get_payload(rows)
            # print(json.dumps(payloads, indent=4))
            sw6 = Sw6Interface(config, 'customer')
            self.logger.info("CustomerService - __category_init - Uploading customers")
            sw6.sync_entity_to_sw(payloads)



        self.__init_callback = lambda rows: __category_init(rows)
        super().__init__(config, db_session, model, self.__init_callback)