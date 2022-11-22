from main import db
import uuid

from main.src.Entity.ERP.NestedDataSets.ERPTaxEntity import ERPTaxEntity

# Make the Tax class


class BridgeTaxEntity(db.Model):
    __tablename__ = 'bridge_tax_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    steuer_schluessel = db.Column(db.Integer(), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    satz = db.Column(db.Float(), nullable=True)
    api_id = db.Column(db.CHAR(36), nullable=False)

    products = db.relationship("BridgeProductEntity", back_populates="tax")

    def __repr__(self):
        return f"Tax {self.description}({self.satz}%)"

    def update_entity(self, entity):
        self.steuer_schluessel = entity.steuer_schluessel
        self.description = entity.description
        self.satz = entity.satz
        return True

    def map_erp_to_db(self, erp_tax: ERPTaxEntity):
        self.steuer_schluessel = erp_tax.get_("StSchl"),
        self.description = erp_tax.get_("Bez"),
        self.satz = erp_tax.get_("Sz")
        # Always keep api_ids
        if not self.api_id:
            self.api_id = uuid.uuid4().hex
        return self
