from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
# For relations
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity

from datetime import datetime


class Bridge2ObjectProductController(Bridge2ObjectController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj

        # Specific Attributes for the child
        self.erp_entity = ERPArtikelEntity(erp_obj=erp_obj)
        self.erp_entity_index_field = 'ArtNr'
        self.bridge_entity = BridgeProductEntity()
        self.bridge_entity_index_field = 'erp_nr'
        self.entity_name = 'product'
        self.filter_expression = "WShopKz = '1'"

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
        self.bridge_entity = None
        self.bridge_entity = BridgeProductEntity()

    def reset_relations(self, bridge_entity):
        """
        Reset all relations and define them new
        all changes - even deleting a relation - will sync with the db
        :param: BridgeEntity
        :return: Updated Bridge Entity
        """
        print("Reset relations - Category", bridge_entity)
        # 1. Categories
        bridge_entity.categories = []
        # Since we have 10 Kategorien we need all between 1 and 11!
        for i in range(1, 11):
            search = "self.erp_entity.get_('ArtKat" + str(i) + "')"
            cat_id = eval(search)
            # Categories must be in db, error
            if cat_id > 0:
                cat_db = BridgeCategoryEntity().query.filter_by(erp_nr=cat_id).first()
                bridge_entity.categories.append(cat_db)

        # 2. Tax
        print("Reset relations - Tax", bridge_entity)
        tax = BridgeTaxEntity().query.filter_by(steuer_schluessel=self.erp_entity.get_('StSchl')).first()
        bridge_entity.tax = tax

        return bridge_entity

    def set_sync_all_range(self):
        self.erp_entity.set_range("000", "ZZZ")

    def set_sync_last_changed_range(self):
        today = datetime.now()
        last_sync = self.bridge_synchronize_entity.dataset_product_sync_date
        test_sync = datetime(2022, 8, 1)
        is_range = self.erp_entity.set_range(test_sync, today, 'LtzAend')

        if is_range:
            return True
        else:
            return False


