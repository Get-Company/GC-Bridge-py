from main import db
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity

class BridgeImageEntity(db.Model):
    --tablename__ = 'bridge_image_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    image_name = db.Column(db.String(255), nullable=True)
    # Standard set the uuid
    sw6_uuid = db.Column(db.CHAR(36), nullable=False)

    # Relations
    category_id = db.Column(db.Integer, db.ForeignKey('bridge_category_entity.id'))
