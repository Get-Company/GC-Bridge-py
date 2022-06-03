from main import db


# Make the Tax class


class BridgeTaxEntity(db.Model):
    __tablename__ = 'bridge_tax_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    steuer_schluessel = db.Column(db.Integer(), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    satz = db.Column(db.Float(), nullable=True)

    products = db.relationship("BridgeProductEntity", back_populates="tax")

    def __repr__(self):
        return f"Tax {self.description}({self.satz}%)"

    def update_entity(self, entity):
        self.steuer_schluessel = entity.steuer_schluessel
        self.description = entity.description
        self.satz = entity.satz
        return True


def map_tax_erp_to_bridge_db(dataset):
    # Mapping the entity
    entity = BridgeTaxEntity(
        steuer_schluessel=dataset.Fields.Item("StSchl").AsInteger,
        description=dataset.Fields.Item("Bez").AsString,
        satz=dataset.Fields.Item("Sz").AsFloat
    )

    return entity
