import requests

from main import db
import uuid
from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy import UniqueConstraint

# Mapping
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity

from pprint import pprint

# Is DataSet Anschrift in ERP
class BridgeCustomerAddressEntity(db.Model):
    __tablename__ = 'bridge_customer_address_entity'
    __table_args__ = (UniqueConstraint('erp_nr', 'erp_ansnr', 'erp_aspnr', name='unique_erp_nr_ansnr_aspnr'),)

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    erp_nr = db.Column(db.CHAR(36), nullable=True)
    erp_ansnr = db.Column(db.Integer(), nullable=True)
    erp_aspnr = db.Column(db.Integer(), nullable=True)
    na1 = db.Column(db.String(255), nullable=False)
    na2 = db.Column(db.String(255), nullable=False)
    na3 = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    str = db.Column(db.String(255), nullable=True)
    plz = db.Column(db.CHAR(12), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    land = db.Column(db.Integer(), nullable=True)
    land_ISO2 = db.Column(db.String(2), nullable=True)
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

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr
        self.erp_ansnr = entity.erp_ansnr
        self.erp_aspnr = entity.erp_aspnr
        self.na1 = entity.na1
        self.na2 = entity.na2
        self.na3 = entity.na3
        self.first_name = entity.first_name
        self.last_name = entity.last_name
        self.title = entity.title
        self.email = entity.email
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

    def map_erp_to_db(self, erp_address_entity: ERPAnschriftenEntity, erp_contact_entity: ERPAnsprechpartnerEntity):
        self.erp_nr = erp_contact_entity.get_('AdrNr')

        self.erp_ansnr = erp_contact_entity.get_('Ansnr')
        if self.erp_ansnr < 0:
            print("Error in ansnr. AdrNr:", self.erp_nr)
            return False

        self.erp_aspnr = erp_contact_entity.get_('AspNr')
        if self.erp_aspnr < 0:
            print("Error in aspnr. AdrNr:", self.erp_nr)
            return False

        self.na1 = erp_address_entity.get_('Na1')
        self.na2 = erp_address_entity.get_('Na2')
        self.na3 = erp_address_entity.get_('Na3')
        self.first_name = erp_contact_entity.get_("VNa")
        self.last_name = erp_contact_entity.get_("NNa")
        self.title = erp_contact_entity.get_("Tit")
        self.email = erp_contact_entity.get_("EMail1")
        self.str = erp_address_entity.get_('Str')
        self.plz = erp_address_entity.get_('PLZ')
        self.city = erp_address_entity.get_('Ort')
        self.land = erp_address_entity.get_('Land')  # !! Integer Germany = 76 ?
        # self.land_ISO2 = self.get_land_ISO2_from_name_by_api(erp_address_entity.get_("LandBez"))
        self.email = erp_address_entity.get_('EMail1')
        self.company = erp_address_entity.get_('Na1')  # !! Do a company check!
        self.erp_ltz_aend = erp_address_entity.get_('LtzAend')
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        return self

    def map_sw5_to_db(self, address):
        self.api_id = address["id"]
        self.erp_nr = address["customer"]["number"]
        if address["company"] is not None and address["company"] != '':
            self.na1 ="Firma"
            self.na2 = address["company"]
        else:
            if address["salutation"] == 'mr':
                self.na1 = "Herr"
            elif address["salutation"] == 'ms':
                self.na1 = "Frau"
            self.na2 = address["firstname"] + " " + address["lastname"]
        self.first_name = address["firstname"]
        self.last_name = address["lastname"]
        self.title = address["title"]
        self.email = address["customer"]["email"]
        self.str = address["street"]
        self.plz = address["zipcode"]
        self.city = address["city"]
        self.land_ISO2 = address["country"]["iso"]
        # Parse Date
        date_firstLogin = datetime.strptime(address["customer"]["changed"], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
        date_changed = datetime.strptime(address["customer"]["changed"], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)

        self.created_at = date_firstLogin
        self.updated_at = date_changed

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

    def map_db_to_erp_anschrift(self):
        updated_fields_list = {
            "AnsNr": self.erp_ansnr,
            "EMail1": self.email,
            "Ort": self.city,
            "PLZ": self.plz,
            "Str": self.str,
            "Na2": self.na2,
            "Na3": self.na3,
        }
        # Standard Billing Address
        if self.customer.erp_reansnr == self.erp_ansnr:
            updated_fields_list["StdReKz"] = 1
        else:
            updated_fields_list["StdReKz"] = 0

        # Standard Shipping Address
        if self.customer.erp_liansnr == self.erp_ansnr:
            updated_fields_list["StdLiKz"] = 1
        else:
            updated_fields_list["StdLiKz"] = 0

        # Company or Private
        if self.customer.ustid:
            updated_fields_list["Na1"] = self.company
        else:
            updated_fields_list["Na1"] = self.na1

        return updated_fields_list

    def map_db_to_erp_ansprechpartner(self):
        anr = ""
        if self.title == "Frau":
            anr = "Frau"
        elif self.title == "Herr":
            anr = "Herrn"

        updated_fields_list = {
            "AnsNr": self.erp_ansnr,
            "AspNr": self.erp_aspnr,
            "Anr": anr,
            "VNa": self.first_name,
            "NNa": self.last_name,
            "EMail1": self.email
        }

        return updated_fields_list

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

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

    def get_address_as_html_row(self):

        html = "<b>" + self.erp_nr + "</b> - "
        if self.company:
            html += self.company + " "
        if self.na1:
            html += self.na1 + " "
        if self.na2:
            html += self.na2 + " "
        if self.na3:
            html += self.na3
        html += self.first_name + " " + self.last_name + " "
        html += self.str + " " + self.plz + " " + self.city + " | " + self.land_ISO2

        if len(html) >= 5:
            return html
        else:
            return "Keine Adresse gefunden!"

    def get_address_as_html_paragraph(self):
        html = "<p>"
        html += self.erp_nr + " "
        if self.company:
            html += self.company + "<br />"
            html += self.na1 + " " + self.na2 + " "
            if self.na3:
                html += self.na3 + "<br />"
        if self.company:
            html += self.company + "<br />"
        if self.na1:
            html += self.na1 + " "
        if self.na2:
            html += self.na2 + " "
        if self.na3:
            html += self.na3
        html += "<br />"
        html += self.first_name + " " + self.last_name + "<br />"
        html += self.str + "<br />"
        html += self.plz + " " + self.city + "<br />"
        html += self.land_ISO2
        html += "</p>"

        return html


    def __repr__(self):
        # text = f"BridgeCustomerAddressEntity ID {self.id}: - {self.na1} {self.na2} {self.na3} - {self.erp_nr}.{self.erp_ansnr}"
        # return text
        return str(vars(self))
