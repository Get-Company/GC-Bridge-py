from main.src.Entity.Mappei.MappeiProductEntity import *
from main.src.Entity.SW6.SW6UpdatingEntity import SW6UpdatingEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from datetime import datetime

class SW6UpdatingController:
    def sync_changed_to_sw(self):
        syncEntity = BridgeSynchronizeEntity().get_entity_by_id_1()
        last_category_update = syncEntity.sw6_category_sync_date
        last_pruduct_update = syncEntity.sw6_product_sync_date
        last_customer_update = syncEntity.sw6_address_sync_date
        options = [
            ['category', BridgeCategoryEntity, last_category_update],
            ['product', BridgeProductEntity, last_pruduct_update],
            #['customer', BridgeAdressenEntity, last_customer_update]
        ]
        for option in options:
            updateController = SW6UpdatingEntity(option[0], option[1], option[2])
            updateController.update_entity()
        syncEntity.sw6_category_sync_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        syncEntity.sw6_product_sync_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        syncEntity.sw6_address_sync_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
