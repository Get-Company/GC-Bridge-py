from main import db
from datetime import datetime


class BridgeSynchronizeEntity(db.Model):
    __tablename__ = 'bridge_synchronize_entity'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
    dataset_category_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    dataset_product_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    dataset_address_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    dataset_tax_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    dataset_order_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    # SW6 Fields
    sw6_category_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    sw6_product_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    sw6_address_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    sw6_order_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    # Loop True or false
    loop_continue = db.Column(db.BOOLEAN, nullable=True)

    def __repr__(self):
        return "BridgeSynchronizeEntity Created/Updated"

    def get_entity_by_id_1(self):
        return self.query.filter_by(id=1).first()
