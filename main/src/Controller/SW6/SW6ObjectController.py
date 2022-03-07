class SW6ObjectController:
    def __init__(self,
                 entity):
        self.entity = entity
        self.id = entity.id

    def upsert_payload(self, id, payload):
        try:
            entity_id = self.get_entity_by_id(id=id)
