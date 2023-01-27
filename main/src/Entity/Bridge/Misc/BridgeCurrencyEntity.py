from main import db
import uuid
from datetime import datetime


# Is DataSet Adressen in ERP
class BridgeCurrencyEntity(db.Model):
    __tablename__ = 'bridge_currency_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    ISO = db.Column(db.VARCHAR(3), nullable=True)
    rate = db.Column(db.Float, nullable=True)
    updated_at = db.Column(db.DateTime(), default=datetime.now())

    def map_api_to_bridge(self, api):
        self.ISO = api["base"]
        self.rate = api["rates"]["EUR"]
        self.updated_at = datetime.now()

        return self

    def update_entity(self, entity):
        self.ISO = entity.ISO
        self.rate = entity.rate
        self.updated_at = datetime.now()




        return self

