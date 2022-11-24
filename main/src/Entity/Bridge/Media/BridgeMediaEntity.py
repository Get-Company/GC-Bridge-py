from main import db
from datetime import datetime

# from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
# from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity

# Media Entity


media_prod = db.Table("bridge_media_prod_entity",
                      db.Column("media_id", db.Integer, db.ForeignKey("bridge_media_entity.id"),
                                primary_key=True),
                      db.Column("product_id", db.Integer, db.ForeignKey("bridge_product_entity.id"),
                                primary_key=True)
                      )

media_cat = db.Table("bridge_media_cat_entity",
                     db.Column("media_id", db.Integer, db.ForeignKey("bridge_media_entity.id"),
                               primary_key=True),
                     db.Column("category_id", db.Integer, db.ForeignKey("bridge_category_entity.id"),
                               primary_key=True)
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
        secondary=media_prod,
        back_populates="medias"
    )

    categories = db.relationship(
        "BridgeCategoryEntity",
        secondary=media_cat,
        back_populates="medias"
    )

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
