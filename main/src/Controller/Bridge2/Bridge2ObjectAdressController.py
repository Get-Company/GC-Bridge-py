from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController

# ERP Entities
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity

# Bridge Entities
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerContactEntity import BridgeCustomerContactEntity

from datetime import datetime


class Bridge2ObjectAddressController(Bridge2ObjectController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj

        # Specific Attributes for the child
        self.erp_entity = ERPAdressenEntity(erp_obj=erp_obj)
        self.erp_entity_index_field = 'AdrNr'
        self.bridge_entity = BridgeCustomerEntity()
        self.bridge_entity_index_field = 'adrnr'
        self.filter_expression = "WShopAdrKz = '1'"
        self.entity_name = 'address'

        super().__init__(
            erp_obj=erp_obj,
            erp_entity=self.erp_entity,
            erp_entity_index_field=self.erp_entity_index_field,
            bridge_entity=self.bridge_entity,
            bridge_entity_index_field=self.bridge_entity_index_field,
            entity_name=self.entity_name,
            filter_expression=self.filter_expression
        )

    def set_sync_all_range(self):
        self.erp_entity.set_range("10000", "69999")

    def set_sync_last_changed_range(self):
        today = datetime.now()
        last_sync = self.bridge_synchronize_entity.dataset_address_sync_date
        test_sync = datetime(2022, 8, 1)
        is_range = self.erp_entity.set_range(test_sync, today, 'LtzAend')
        if is_range:
            return True
        else:
            return False
