from main import db
import uuid
from datetime import datetime

# Mapping
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity

# Relations
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity


# Is DataSet Adressen in ERP
class BridgeCustomerEntity(db.Model):
    __tablename__ = 'bridge_customer_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False, default=uuid.uuid4().hex)
    erp_nr = db.Column(db.CHAR(36), nullable=True, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    ustid = db.Column(db.String(255), nullable=True)
    erp_reansnr = db.Column(db.Integer(), nullable=True)
    erp_liansnr = db.Column(db.Integer(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.now())

    """
    Relations
    """
    # Relation one - to -many
    addresses = db.relationship(
        'BridgeCustomerAddressEntity',
        back_populates="customer",
        lazy=True,
        cascade="all, delete, delete-orphan"
    )

    # Relation one - to -many
    orders = db.relationship(
        'BridgeOrderEntity',
        back_populates="customer")

    def get_entity_id_field(self):
        """
        This is needed in the controller. The controller self.upsert/self.is_in_db looks for the field in the db
        whether the entity is already in the db or not
        """
        return self.erp_nr

    def get_default_shipping_address(self):
        try:
            shipping_address = self.addresses[self.erp_liansnr]
            return shipping_address

        except "NoneType":
            print("Standard Shipping Address not found")

    def get_default_billing_address(self):
        try:
            billing_address = self.addresses[self.erp_reansnr]
            return billing_address

        except AttributeError:
            print("Standard Billing Address not found")

    def update_entity(self, entity):
        """
        Update the current object with the values of another object.

        :param entity: The object to update the current object with.
        :type entity: Any object
        :return: The updated object.
        :rtype: Any object
        """
        self.erp_nr = entity.erp_nr
        self.ustid = entity.ustid
        self.erp_reansnr = entity.erp_reansnr
        self.erp_liansnr = entity.erp_liansnr
        self.api_id = entity.api_id or uuid.uuid4().hex
        self.email = entity.email
        self.updated_at = entity.updated_at

        return self

    def map_erp_to_db(self, erp_entity: ERPAdressenEntity):
        self.erp_nr = erp_entity.get_('AdrNr')
        self.ustid = erp_entity.get_("UStId")
        self.erp_reansnr = erp_entity.get_("ReAnsNr")
        self.erp_liansnr = erp_entity.get_("LiAnsNr")
        if erp_entity.get_("WShopID"):
            self.api_id = erp_entity.get_("WShopID")
        # Update Date Fields
        updated = erp_entity.get_('LtzAend')
        self.updated_at = updated

        self.email = erp_entity.get_login()
        print(self.email)

        return self

    def map_db_to_erp(self):
        """
        We just need a list of the erp fields and their new value
        :return: dict of fields
        """
        updated_fields_list = {
            "ReAnsNr": self.erp_reansnr,
            "LiAnsNr": self.erp_liansnr,
            "LtzAend": self.updated_at,
            "WShopAdrKz": 1,
            "WShopID": self.api_id
        }
        if self.ustid:
            updated_fields_list["UStId"] = self.ustid

        return updated_fields_list

    def map_sw6_to_db(self, customer: dict):
        self.erp_nr = customer['customerNumber']
        self.api_id = customer['id']
        self.ustid = customer['vatIds'][0]
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        return self

    def map_sw5_to_db(self, customer: list):
        self.erp_nr = customer['number']
        self.api_id = customer['id']
        self.ustid = customer['defaultBillingAddress']['vatId']
        self.email = customer["email"]
        # Parse Date
        date_firstLogin = self._get_date_or_none(customer["firstLogin"])
        date_changed = self._get_date_or_none(customer["changed"])
        self.created_at = date_firstLogin
        self.updated_at = date_changed

        self.erp_reansnr = 0
        self.erp_liansnr = 0

        def _find_address_index(customer):
            for index, address in enumerate(customer["addresses"]):
                if address["id"] == customer["defaultBillingAdress"]["id"]:
                    self.erp_reansnr = index

                if address["id"] == customer["defaultShippingAddress"]["id"]:
                    self.erp_liansnr = index

        return self

    def map_db_to_sw5(self, customer):
        pass

    def _get_date_or_none(self, date):
        if date:
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
        else:
            return None

    def __repr__(self):
        # text = f"BridgeCustomerEntity: {self.id} - {self.erp_nr}"
        # return text
        return str(vars(self))
