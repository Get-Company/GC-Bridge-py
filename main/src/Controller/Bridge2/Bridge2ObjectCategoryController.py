from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
from main.src.Entity.ERP.ERPArtikelKategorieEntity import ERPArtikelKategorieEntity
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
# Relations
from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaEntity

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

    def reset_relations(self, bridge_entity):
        """
        Reset all relations and define them new
        all changes - even deleting a relation - will sync with the db
        :param: BridgeEntity
        :return: Updated Bridge Entity
        """
        print("Reset relations - Media", bridge_entity)
        # 3. Media
        bridge_entity.medias = []

        img = self.erp_entity.get_images()

        if img:
            # 3.1 Check if media in db - update or insert
            media_in_db = BridgeMediaEntity().query.filter_by(filename=img["name"]).one_or_none()

            # 3.2 Query Media
            if media_in_db is None:
                media_to_insert = BridgeMediaEntity()
            else:
                media_to_insert = media_in_db

            media_to_insert.filename = img["name"]
            media_to_insert.filetype = img["type"]
            media_to_insert.description = bridge_entity.title
            media_to_insert.path = 'https://www.classei.de/images/categories/'

            bridge_entity.medias.append(media_to_insert)
        else:
            pass

        return bridge_entity