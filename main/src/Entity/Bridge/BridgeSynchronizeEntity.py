from main import db
from datetime import datetime


class BridgeSynchronizeEntity(db.Model):
    __tablename__ = 'bridge_synchronize_entity'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
    dataset_category_sync_date = db.Column(db.DateTime(), nullable=True)
    dataset_product_sync_date = db.Column(db.DateTime(), nullable=True)
    dataset_address_sync_date = db.Column(db.DateTime(), nullable=True)
    dataset_tax_sync_date = db.Column(db.DateTime(), nullable=True)
    # SW6 Fields
    sw6_category_sync_date = db.Column(db.DateTime(), nullable=True)
    sw6_product_sync_date = db.Column(db.DateTime(), nullable=True)
    sw6_address_sync_date = db.Column(db.DateTime(), nullable=True)

    def __repr__(self):
        return "BridgeSynchronizeEntity Created/Updated"

    def get_entity_by_id_1(self):
        return self.query.filter_by(id=1).first()
