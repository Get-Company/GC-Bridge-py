import uuid
import json

from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from uuid import UUID


class SW6ProductEntity:

    def map_db_to_sw6(self, ntt, add_parent=True):
        print("SW6ProductEntity.map_db_to_sw6 - %s" % ntt.name)
        payload = self.map_standard_fields_db_to_sw6(ntt)
        return payload

    def map_standard_fields_db_to_sw6(self, ntt):
        categories = ntt.categories
        payload = {
            "id": ntt.api_id,
            "name": ntt.name,
            "productNumber": ntt.erp_nr,
            "stock": 10,
            # Attention Small Caps!!!!!!
            "taxId": "e495f3d715a04968bd0820dafe191aa8",
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": [
                {
                    "id": categories[0].api_id,
                    "name": categories[0].translations[0].title,
                    "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "displayNestedProducts": True,
                    "productAssignmentType": "product",
                    "type": "page",
                    "description": categories[0].description
                }
            ],
            "price": [
                {
                    # Attention Small Caps!!!!!!
                    "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
                    "gross": ntt.price * 1.19,
                    "net": ntt.price,
                    "linked": True
                }
            ],
            "cmsPageId": "7a6d253a67204037966f42b0119704d5"
        }

        return payload
