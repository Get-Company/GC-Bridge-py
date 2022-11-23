from main import db
import uuid
from datetime import datetime

# Mapping
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity

# Relations
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerContactEntity import BridgeCustomerContactEntity


# Is DataSet Adressen in ERP
class BridgeCustomerEntity(db.Model):
    __tablename__ = 'bridge_customer_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    erp_nr = db.Column(db.Integer(), nullable=False)
    erp_ltz_aend = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    """
    Relations
    """
    # Relation one - to -many
    addresses = db.relationship(
        'BridgeCustomerAddressEntity',
        back_populates="customer")

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr
        self.erp_ltz_aend = entity.erp_ltz_aend

        return self

    def map_erp_to_db(self, erp_entity: ERPAdressenEntity):
        self.erp_nr = erp_entity.get_('AdrNr')
        self.erp_ltz_aend = erp_entity.get_('LtzAend')
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        return self

    def __repr__(self):
        text = f"BridgeCustomerEntity: {self.id} - {self.erp_nr}"
        return text
