
from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
import sqlalchemy

# ERP Entities
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity

# Bridge Entities
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerContactEntity import BridgeCustomerContactEntity

# Controller
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerContactController import \
    Bridge2ObjectCustomerContactController
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerAddressController import \
    Bridge2ObjectCustomerAddressController
from datetime import datetime

import pprint

class Bridge2ObjectCustomerController(Bridge2ObjectController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj

        # Specific Attributes for the child
        self.erp_entity = ERPAdressenEntity(erp_obj=erp_obj)
        self.erp_entity_index_field = 'AdrNr'
        self.bridge_entity = BridgeCustomerEntity()
        self.bridge_entity_index_field = 'erp_nr'
        self.filter_expression = "WShopAdrKz = '1'"
        self.entity_name = 'address'
        #
        super().__init__(
            erp_obj=erp_obj,
            erp_entity=self.erp_entity,
            erp_entity_index_field=self.erp_entity_index_field,
            bridge_entity=self.bridge_entity,
            bridge_entity_index_field=self.bridge_entity_index_field,
            entity_name=self.entity_name,
            filter_expression=self.filter_expression
        )

    def set_sync_all_range(self):
        self.erp_entity.set_range("10000", "69999")

    def set_sync_last_changed_range(self):
        today = datetime.now()
        last_sync = self.bridge_synchronize_entity.dataset_address_sync_date
        test_sync = datetime(2022, 8, 1)
        is_range = self.erp_entity.set_range(test_sync, today, 'LtzAend')
        if is_range:
            return True
        else:
            return False

    def set_bridge_entity(self):
        """
        Necessary for each child, since the sync loop needs to set the entity on each run
        :return:
        """
        self.bridge_entity = BridgeCustomerEntity()

    def reset_relations(self, bridge_entity: BridgeCustomerEntity):
        # 1. Addresses
        # print(bridge_entity.addresses)
        # bridge_entity.addresses = []
        addresses_erp = self.erp_entity.get_anschriften()
        while not addresses_erp.range_eof():
            adr_nr = addresses_erp.get_("AdrNr")
            ans_nr = addresses_erp.get_("AnsNr")

            address_erp = BridgeCustomerAddressEntity().query.filter_by(
                erp_nr=adr_nr
            ).filter_by(
                erp_ansnr=ans_nr
            ).one_or_none()
            print(address_erp)

            if address_erp is not None:
                bridge_entity.addresses.append(address_erp)
            else:
                pass

            addresses_erp.range_next()

        # self.logger.debug("Reset Relations", bridge_entity.addresses)
        return bridge_entity

    def is_in_db(self):
        """
        Check if the entity is in db. Use the standard ERP id field = 'ArtNr' and standard DB id field = erp_nr for Artikel
        The code example would look like:
        self.bridge_entity.query.filter_by(erp_nr=104014).first()
        erp=104014:
            bridge_entity_index_field = self.erp_entity.get_(self.erp_entity_index_field))
        :return: object
        """
        bridge_entity_index_field = self.bridge_entity_index_field
        if bridge_entity_index_field:
            try:
                in_db = self.bridge_entity.query.filter_by(
                    erp_nr=self.erp_entity.get_("AdrNr")).one_or_none()

                if in_db:
                    return in_db
                else:
                    return None

            except sqlalchemy.exc.MultipleResultsFound:
                print("Multiple results for:")
                print("AdrNr:", self.erp_entity.get_("AdrNr"))
                return False

    def commit_session(self):
        try:
            self.db.session.commit()
            print("\033[92m Success - Customer:", self.erp_entity.get_("AdrNr"), '\033[0m')
        except:
            print("\033[91m Fail - Customer:", self.erp_entity.get_("AdrNr"), '\033[0m')

