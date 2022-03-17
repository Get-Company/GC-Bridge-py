from main.src.Entity.Bridge.Product.BridgeProductEntity import *


class SW6ProductEntity:

    def map_db_to_sw6(self, ntt: BridgeProductEntity, add_parent=True):

        payload = self.map_fields_db_to_sw6(ntt)
        return payload

    def map_fields_db_to_sw6(self, ntt):
        payload = {
            "id": ntt.api_id,
            "name": ntt.translations[0].name,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price": [
                {"currencyId": 'B7D2554B0CE847CD82F3AC9BD1C0DFCA',
                 "gross": int(ntt.price * 1.19),
                 "net": int(ntt.price),
                 "linked": True}],
            "productNumber": ntt.erp_nr,
            "stock": 999999,
            "taxId": '679E8B0D9111461BB153D9EDEA757BFA'
        }

        ntt_categories = ntt.categories
        for category in ntt_categories:
            cat_ids = [category.api_id]
        payload["categoryIds"] = cat_ids

        return payload


