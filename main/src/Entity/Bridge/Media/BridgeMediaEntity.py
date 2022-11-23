from main import db
from datetime import datetime
#from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity

# Media Entity


media_product = db.Table("bridge_media_product_entity",
                         db.Column("media_id", db.Integer, db.ForeignKey("bridge_media_entity.id"),
                                   primary_key=False),
                         db.Column("product_id", db.Integer, db.ForeignKey("bridge_product_entity.id"),
                                   primary_key=False)
                         )


class BridgeMediaEntity(db.Model):
    __tablename__ = "bridge_media_entity"

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    path = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    products = db.relationship(
        "BridgeProductEntity",
        secondary=media_product,
        back_populates="medias")

    def update_entity(self, entity):
        """
        The entity is produced by ERP. Simply use the same names
        self.hans = entity.hans
        """
        self.path = entity.path
        self.filename = entity.filename
        self.filetype = entity.filetype
        self.description = entity.description

        return self

    # categories = db.relationship(
    #     "BridgeCategoryEntity",
    #     secondary=media_category,
    #     back_populates="categories"
