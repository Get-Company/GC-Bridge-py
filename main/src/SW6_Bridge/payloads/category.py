from main.src.SW6_Bridge.payloads import Payload
import json

class CategoryPayload(Payload):
    def __init__(self, config):
        create_payload = lambda db_row: {
            "id": db_row.api_id,
            "name": db_row.title,
            "createdAt": db_row.erp_ltz_aend,
            "displayNestedProducts": True,
            "productAssignmentType": "product",
            "type": "page",
            "description": db_row.description,
            "parentId": db_row.api_idparent
        }
        super().__init__(self, config, create_payload)

    


