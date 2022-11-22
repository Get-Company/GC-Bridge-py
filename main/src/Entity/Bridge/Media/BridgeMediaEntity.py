from main import db
from datetime import datetime
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity

#
# class BridgeMediaEntity(db.Model):
#     __tablename__ = 'bridge_media_entity'
#
#     id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
#     sw6_uuid = db.Column(db.CHAR(36), nullable=True)
#     media_path = db.Column(db.TEXT(), nullable=False)
#     media_name = db.Column(db.TEXT(), nullable=False)
#     description = db.Column(db.TEXT(), nullable=True)
#     created_at = db.Column(db.DateTime(), default=datetime.now())
#     media_relation = db.relationship("BridgeMediaRelations", back_populates="media")
#
#     def __repr__(self):
#         return f"Media {self.media_name} was created"
#
#     def update_entity(self, entity):
#         self.sw6_uuid = entity.sw6_uuid
#         self.media_path = entity.media_path
#         self.media_name = entity.media_name
#         self.description = entity.description
#         # self.sw6_uuid = entity['sw6_uuid']
#         # self.media_path = entity['media_path']
#         # self.media_name = entity['media_name']
#         # self.description = entity['description']
#         db.session.commit()
#         return True

"""
Problem!!
Wenn nicht überprüft wird, ob das Bild bereits als relation existiert,
wird es mehrfach als relation angelegt. 
Vor dem Zuordnen des Bildes zum Product, muss MediaEntity abgefragt werden!
"""
#
# class BridgeMediaRelations(db.Model):
#     __tablename__ = "bridge_media_relations"
#     id = db.Column(db.Integer, primary_key=True)
#     media_id = db.Column(db.Integer, db.ForeignKey("bridge_media_entity.id"), nullable=False)
#     category_id = db.Column(db.Integer, db.ForeignKey("bridge_category_entity.id"), nullable=True)
#     product_id = db.Column(db.Integer, db.ForeignKey("bridge_product_entity.id"), nullable=True)
#
#     # __table_args__ = (db.UniqueConstraint(category_id, product_id, media_id),)
#
#     category = db.relationship("BridgeCategoryEntity", back_populates="media_relations")
#     product = db.relationship("BridgeProductEntity", back_populates="media_relations")
#     media = db.relationship("BridgeMediaEntity")
#
#     def add_new_relation_record(self, params): # TEST UPLOAD!!!!!!!!!!!!
#         media = BridgeMediaEntity.query.where(BridgeMediaEntity.media_name == params['media_name']).first()
#         category = None
#         product = None
#         if 'category_title' in params.keys():
#             category = BridgeCategoryEntity.query.where(BridgeCategoryEntity.title == params['category_title']).first()
#         if 'product_name' in params.keys():
#             product = BridgeProductEntity.query.where(BridgeProductEntity.name == params['product_name']).first()
#
#         media_relations = BridgeMediaRelations(media=media, category=category, product=product)
#         db.session.add(media_relations)
#         db.session.commit()
#         print("Media relation has been created successfully")



