from main import db
import uuid
from datetime import datetime

# Mapping
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerContactEntity import BridgeCustomerContactEntity


# Is DataSet Anschrift in ERP
class BridgeCustomerAddressEntity(db.Model):
    __tablename__ = 'bridge_customer_address_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    erp_nr = db.Column(db.Integer(), nullable=False)
    erp_ansnr = db.Column(db.Integer(), nullable=False)
    na1 = db.Column(db.String(255), nullable=False)
    na2 = db.Column(db.String(255), nullable=False)
    na3 = db.Column(db.String(255), nullable=True)
    str = db.Column(db.String(255), nullable=True)
    plz = db.Column(db.CHAR(12), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    land = db.Column(db.Integer(), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    """
    Relations
    """

    # Customer aka DataSet Adressen many - to -one
    customer = db.relationship('BridgeCustomerEntity', back_populates='addresses')
    customer_id = db.Column(db.Integer(), db.ForeignKey('bridge_customer_entity.id'))

    # Contact aka DataSet Ansprechpartner one - to - many
    contacts = db.relationship('BridgeCustomerContactEntity', back_populates='address')

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr
        self.erp_ansnr = entity.erp_ansnr
        self.na1 = entity.na1
        self.na2 = entity.na2
        self.na3 = entity.na3
        self.str = entity.str
        self.plz = entity.plz
        self.city = entity.city
        self.land = entity.land
        self.email = entity.email
        self.company = entity.company

        return self

    def map_erp_to_db(self, erp_entity: ERPAnschriftenEntity):
        self.erp_nr = erp_entity.get_('AdrNr')
        self.erp_ansnr = erp_entity.get_('AnsNr')
        self.na1 = erp_entity.get_('Na1')
        self.na2 = erp_entity.get_('Na2')
        self.na3 = erp_entity.get_('Na3')
        self.str = erp_entity.get_('Str')
        self.plz = erp_entity.get_('PLZ')
        self.city = erp_entity.get_('Ort')
        self.land = erp_entity.get_('Land')  # !! Integer Germany = 76 ?
        self.email = erp_entity.get_('EMail1')
        self.company = erp_entity.get_('Na1')  # !! Do a company check!
        self.erp_ltz_aend = erp_entity.get_('LtzAend')
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        return self

    def __repr__(self):
        text = f"BridgeCustomerAddressEntity ID {self.id}: - {self.na1} {self.na2} {self.na3} - {self.erp_nr}.{self.erp_ansnr}"
        return text

