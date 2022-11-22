from main import db
import uuid
from datetime import datetime

# Mapping
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity


# Is DataSet Ansprechpartner in ERP
class BridgeCustomerContactEntity(db.Model):
    __tablename__ = 'bridge_customer_contact_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    erp_nr = db.Column(db.Integer(), nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    erp_ansnr = db.Column(db.Integer(), nullable=False)
    erp_aspnr = db.Column(db.Integer(), nullable=False)
    erp_ltz_aend = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    """
    Relations
    """

    # Address aka DataSet Anschriften many - to - one
    address = db.relationship('BridgeCustomerAddressEntity', back_populates='contacts')
    address_id = db.Column(db.Integer(), db.ForeignKey('bridge_customer_address_entity.id'))

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr
        self.first_name = entity.first_name
        self.last_name = entity.last_name
        self.title = entity.title
        self.email = entity.email
        self.erp_ansnr = entity.erp_ansnr
        self.erp_aspnr = entity.erp_aspnr

        return self

    def map_erp_to_db(self, erp_entity: ERPAnsprechpartnerEntity):
        self.erp_nr = erp_entity.get_('AdrNr')
        self.first_name = erp_entity.get_('VNa')
        self.last_name = erp_entity.get_('NNa')
        self.title = erp_entity.get_('Tit')
        self.email = erp_entity.get_('EMail1')
        self.erp_ltz_aend = erp_entity.get_('LtzAend')
        self.erp_ansnr = erp_entity.get_("AnsNr")
        self.erp_aspnr = erp_entity.get_("AspNr")
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        return self

    def __repr__(self):
        text = f"BridgeCustomerContactEntity ID {self.id}: - {self.first_name} {self.last_name} - {self.erp_nr}.{self.erp_ansnr}.{self.erp_aspnr}"
        return text
