from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
from main.src.Entity.ERP.ERPArtikelKategorieEntity import ERPArtikelKategorieEntity
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity

from datetime import datetime


class Bridge2ObjectCategoryController(Bridge2ObjectController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj

        # Specific Attributes for the child
        self.erp_entity = ERPArtikelKategorieEntity(erp_obj=erp_obj)
        self.erp_entity_index_field = 'Nr'
        self.bridge_entity = BridgeCategoryEntity()
        self.bridge_entity_index_field = 'erp_nr'
        self.entity_name = 'category'
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
        self.bridge_entity = BridgeCategoryEntity()

    def reset_relations(self, entity_db):
        """ The relations should be set in the product so nothing to do here"""
        return entity_db

    def set_sync_all_range(self):
        self.erp_entity.set_range("0", "999999", "Nr")

    def set_sync_last_changed_range(self):
        today = datetime.now()
        last_sync = self.bridge_synchronize_entity.dataset_category_sync_date
        test_sync = datetime(2022, 1, 1)
        is_range = self.erp_entity.set_range(test_sync, today, 'LtzAend')
        if is_range:
            return True
        else:
            return False



