from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from os import path


class SW6CategoryEntity:

    def map_db_to_sw6(self, ntt: BridgeCategoryEntity, add_parent=True):

        payload = self.map_fields_db_to_sw6(ntt)

        if add_parent:
            payload = self.add_parent_to_sw6(ntt, payload)

        return payload

    def map_fields_db_to_sw6(self, ntt):
        payload = {
            "id": ntt.api_id,
            "name": ntt.translations[0].title,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "displayNestedProducts": True,
            "productAssignmentType": "product",
            "type": "page",
            "description": ntt.description
        }

        return payload

    def add_parent_to_sw6(self, ntt, payload):
        ntt_parent = BridgeCategoryEntity.query.filter_by(api_id=ntt.api_idparent).first()
        if ntt_parent:
            print("Parent of %s is %s." % (ntt.title, ntt_parent.title))
            payload["parent"] = self.map_fields_db_to_sw6(ntt_parent)
        return payload

    def add_image_to_sw6(self, ntt):
        img = ntt.img
        payload = {
            "name": ntt.title,

        }


