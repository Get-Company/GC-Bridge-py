from main.src.SW6_Bridge.modells import db

class Payload:
    def __init__(self, type, config, create_payload):
        self.type = type
        self.config = config
        self.create_payload = create_payload

    def get_payload(self, db_rows):
        payloads = [self.create_payload(db_row) for db_row in db_rows]
        return payloads