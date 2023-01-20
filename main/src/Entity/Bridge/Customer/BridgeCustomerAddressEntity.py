import requests

from main import db
import uuid
from datetime import datetime
from sqlalchemy.orm import backref

# Mapping
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerContactEntity import BridgeCustomerContactEntity

# Is DataSet Anschrift in ERP
class BridgeCustomerAddressEntity(db.Model):
    __tablename__ = 'bridge_customer_address_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    erp_nr = db.Column(db.CHAR(10), nullable=True)
    erp_ansnr = db.Column(db.Integer(), nullable=True)
    erp_aspnr = db.Column(db.Integer(), nullable=True)
    na1 = db.Column(db.String(255), nullable=False)
    na2 = db.Column(db.String(255), nullable=False)
    na3 = db.Column(db.String(255), nullable=True)
    str = db.Column(db.String(255), nullable=True)
    plz = db.Column(db.CHAR(12), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    land = db.Column(db.Integer(), nullable=True)
    land_ISO2 = db.Column(db.String(2), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())  # Delete and refactor
    updated_at = db.Column(db.DateTime(), default=datetime.now())

    """
    Relations
    """

    # Customer aka DataSet Adressen many - to -one
    customer = db.relationship('BridgeCustomerEntity', back_populates='addresses')
    customer_id = db.Column(db.Integer(), db.ForeignKey('bridge_customer_entity.id'))

    # Contact aka DataSet Ansprechpartner one - to - many
    contacts = db.relationship('BridgeCustomerContactEntity', back_populates='address')

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr
        self.erp_ansnr = entity.erp_ansnr
        self.erp_aspnr = entity.erp_aspnr
        self.na1 = entity.na1
        self.na2 = entity.na2
        self.na3 = entity.na3
        self.str = entity.str
        self.plz = entity.plz
        self.city = entity.city
        self.land = entity.land
        self.land_ISO2 = entity.land_ISO2
        self.email = entity.email
        self.company = entity.company
        self.erp_ltz_aend = entity.erp_ltz_aend
        self.updated_at = datetime.now()

        return self

    def map_erp_to_db(self, erp_entity: ERPAnschriftenEntity):
        self.erp_nr = erp_entity.get_('AdrNr')
        self.erp_ansnr = erp_entity.get_('Ansnr')
        self.erp_aspnr = erp_entity.get_('AspNr')
        self.na1 = erp_entity.get_('Na1')
        self.na2 = erp_entity.get_('Na2')
        self.na3 = erp_entity.get_('Na3')
        self.str = erp_entity.get_('Str')
        self.plz = erp_entity.get_('PLZ')
        self.city = erp_entity.get_('Ort')
        self.land = erp_entity.get_('Land')  # !! Integer Germany = 76 ?
        self.land_ISO2 = self.get_land_ISO2_from_name_by_api(erp_entity.get_("LandBez"))
        self.email = erp_entity.get_('EMail1')
        self.company = erp_entity.get_('Na1')  # !! Do a company check!
        self.erp_ltz_aend = erp_entity.get_('LtzAend')
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        return self

    def map_sw6_to_db(self, customer, address=None):
        self.erp_nr = customer["customerNumber"]
        self.api_id = uuid.uuid4().hex
        if customer["company"]:
            self.na1 = "Firma"
            self.na2 = customer["company"]
            self.company = customer["company"]
        else:
            # Todo: Languages? Salutation is english.
            self.na1 = address["salutation"]["displayName"]
            self.na2 = address["firstName"] + " " + address["lastName"]
        if address["additionalAddressLine1"]:
            self.na3 = address["additionalAddressLine1"]

        if address["additionalAddressLine1"]:
            self.na3 = self.na3 + " | " + address["additionalAddressLine1"]

        self.str = address["street"]
        self.plz = address["zipcode"]
        self.land_ISO2 = address["country"]["iso"]
        self.email = customer["email"]

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        return self

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def get_default_contact(self):
        contact = self.contacts[self.erp_aspnr]

        return contact

    def get_land_ISO2_from_name_by_api(self, name):
        """
        #TODO: Make it more efficient. Now it always asks the api.
        Setup a list of countries in an extra table?
        :param name:
        :return:
        """
        url = f"http://api.geonames.org/searchJSON?q={name}&maxRows=1&username=buchner"
        response = requests.get(url)
        data = response.json()
        return data['geonames'][0]['countryCode']

    def __repr__(self):
        # text = f"BridgeCustomerAddressEntity ID {self.id}: - {self.na1} {self.na2} {self.na3} - {self.erp_nr}.{self.erp_ansnr}"
        # return text
        return str(vars(self))
