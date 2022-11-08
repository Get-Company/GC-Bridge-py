from main.src.Entity.Bridge.Category import BridgeCategoryEntity

from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity
from main.src.Entity.ERP.ERPArtikelKategorieEntity import ERPArtikelKategorieEntity

from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

from datetime import datetime

def update_category(id="2"):

    bridge_sync = BridgeSynchronizeEntity().get_entity_by_id_1()
    last_dataset_sync = bridge_sync.dataset_category_sync_date
    last_sw6_sync = bridge_sync.sw6_category_sync_date
    now = datetime.now()

    print(last_dataset_sync, last_sw6_sync)

    bridge_category = BridgeCategoryEntity.query.filter_by(id=id).first()
    erp_obj = ERPConnectionEntity(mandant="58")
    erp_category = ERPArtikelKategorieEntity(erp_obj=erp_obj, id_value=id)

