from main.src.Controller.ERP.ERPController import ERPController
from main.src.Entity.ERP.NestedDataSets.ERPCurrencyEntity import ERPCurrencyEntity
from main.src.Entity.Bridge.Misc.BridgeCurrencyEntity import BridgeCurrencyEntity


class ERPCurrencyController(ERPController):

    def __init__(self, erp_obj):
        self.erp_obj = erp_obj
        self.erp_entity = ERPCurrencyEntity(erp_obj=erp_obj)
        self.bridge_entity = BridgeCurrencyEntity

    def update_currency(self, iso3="CHF"):
        self.erp_entity.get_iso3(iso3)
        currency = self.bridge_entity.query.filter_by(ISO=iso3).one_or_none()
        self.erp_entity.set_currency(currency)

