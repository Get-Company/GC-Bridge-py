from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
from main.src.Entity.ERP.NestedDataSets.ERPTaxEntity import ERPTaxEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity

from datetime import datetime


class Bridge2ObjectTaxController(Bridge2ObjectController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj

        # Specific Attributes for the child
        self.erp_entity = ERPTaxEntity(erp_obj=erp_obj)
        self.erp_entity_index_field = 'StSchl'
        self.bridge_entity = BridgeTaxEntity()
        self.bridge_entity_index_field = 'steuer_schluessel'
        self.entity_name = 'tax'
        self.filter_expression = None

        super().__init__(
            erp_obj=erp_obj,
            erp_entity=self.erp_entity,
            erp_entity_index_field=self.erp_entity_index_field,
            bridge_entity=self.bridge_entity,
            bridge_entity_index_field=self.bridge_entity_index_field,
            entity_name=self.entity_name,
            filter_expression=self.filter_expression
        )

    def set_bridge_entity(self):
        """
        Necessary for each child, since the sync loop needs to set the entity on each run
        :return:
        """
        self.bridge_entity = BridgeTaxEntity()

    def set_sync_all_range(self):
        self.erp_entity.set_nested_range('0', '99')

    def set_sync_last_changed_range(self):
        today = datetime.now()
        last_sync = self.bridge_synchronize_entity.dataset_product_sync_date
        test_sync = datetime(2022, 8, 1)
        is_range = self.erp_entity.set_nested_range(test_sync, today, 'AendDat')
        if is_range:
            return True
        else:
            return False
