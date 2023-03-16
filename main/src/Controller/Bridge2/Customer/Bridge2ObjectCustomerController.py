from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
import sqlalchemy

# ERP Entities
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity

# Bridge Entities
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

# Controller
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerAddressController import \
    Bridge2ObjectCustomerAddressController
from datetime import datetime

from pprint import pprint


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
        last_sync = self.bridge_synchronize_entity.get_entity_by_id_1().dataset_customers_sync_date
        test_sync = datetime(2023, 1, 19, 13, 40)
        print("Sync Range:", last_sync.strftime("%d.%m.%Y %H:%M:%S"), today.strftime("%d.%m.%Y %H:%M:%S"))
        is_range = self.erp_entity.set_range(start=last_sync, end=today, field='LtzAend')
        if is_range:
            return True
        else:
            return False

    def sync_all(self):
        self.set_sync_all_range()
        # Filter the results
        self.apply_filter()
        self.upsert()
        return True

    def sync_changed(self):
        is_ranged = self.set_sync_last_changed_range()
        if is_ranged:
            # Filter the results
            self.erp_entity.filter_expression("")
            # Not really nice but we need quick results
            # Every Address and Contact must be synced by itself
            Bridge2ObjectCustomerAddressController(erp_obj=self.erp_obj).sync_range(start=self.erp_entity.get_("AdrNr"), end=self.erp_entity.get_("AdrNr"))
            self.upsert()
            return True

    def before_upsert(self, current_erp_entity):
        Bridge2ObjectCustomerAddressController(
            erp_obj=self.erp_obj).sync_range(
            start=current_erp_entity.get_("AdrNr"),
            end=current_erp_entity.get_("AdrNr")
        )
        return True

    def set_bridge_entity(self):
        """
        Necessary for each child, since the sync loop needs to set the entity on each run
        :return:
        """
        self.bridge_entity = BridgeCustomerEntity()

    def reset_relations(self, bridge_entity: BridgeCustomerEntity):
        # 1. Addresses
        # print(bridge_entity.addresses)
        bridge_entity.addresses = []
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

        # Set default Addresses shipping/billing
        erp_nr = addresses_erp.get_("AdrNr")

        shipping_address_erp_id = self.erp_entity.get_("LiAnsNr")
        shipping_address_entity = BridgeCustomerAddressEntity().query.filter_by(
            erp_nr=erp_nr
        ).filter_by(
            erp_ansnr=shipping_address_erp_id
        ).one_or_none()

        bridge_entity.default_shipping_address = shipping_address_entity

        billing_address_erp_id = self.erp_entity.get_("ReAnsNr")
        billing_address_entity = BridgeCustomerAddressEntity().query.filter_by(
            erp_nr=erp_nr
        ).filter_by(
            erp_ansnr=billing_address_erp_id
        ).one_or_none()

        bridge_entity.default_billing_address = billing_address_entity

        return bridge_entity

    def is_in_db(self):
        """
        Check if the entity is in db. Use the standard ERP id field = 'ArtNr' and standard DB id field = erp_nr for Artikel
        The code example would look like:
        self.bridge_entity.query.filter_by(erp_nr=104014).first()
        erp=104014:
            bridge_entity_index_field = self.erp_entity.get_(self.erp_entity_index_field)
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

    def commit_session(self, info=None):
        try:
            self.commit_with_errors()
            print("\033[92m Success - Customer:", info, '\033[0m')
        except Exception as e:
            print("\033[91m Fail - Customer:", info, '\033[0m')
            print(e)

    def upsert_from_sw6(self, customer: dict):
        converted_bridge_customer_entity = self.convert_customer_from_sw6_to_bridge_entity(customer=customer)
        # 1 New/Old Customer
        bridge_customer_entity = BridgeCustomerEntity()
        customer_in_db = bridge_customer_entity.query.filter_by(erp_nr=customer["customerNumber"]).one_or_none()

        if customer_in_db:
            print("Old customer:", customer["customerNumber"])
            updated_bridge_customer_entity = customer_in_db.update_entity(converted_bridge_customer_entity)
            self.db.session.add(updated_bridge_customer_entity)
            pprint(updated_bridge_customer_entity)
        else:
            print("New customer:", customer["customerNumber"])
            pprint(converted_bridge_customer_entity)
            self.db.session.add(converted_bridge_customer_entity)

        # Here we set the attribute/field of dataset_NAME_sync_date by the entity_name
        # We need to set it BEFORE the sync. So we can query the db for the last sync session
        # by range last_sync - now()
        setattr(self.bridge_synchronize_entity, 'sw6_' + self.entity_name + '_sync_date', datetime.now())
        self.db.session.add(self.bridge_synchronize_entity)

        self.commit_session(info=customer["customerNumber"])
        return True

    """
    Special Tasks
    """

    def get_customer_new_or_updated_since_last_sync_from_erp(self):
        last_customer_sync = BridgeSynchronizeEntity().get_entity_by_id_1().dataset_customers_sync_date

    def convert_customer_from_sw6_to_bridge_entity(self, customer: dict):
        """
        No relations are checked or updated. Simply transform sw6 to bridge db
        :param customer:
        :return:
        """
        bridge_customer_entity = BridgeCustomerEntity()

        mapped_customer = bridge_customer_entity.map_sw6_to_db(customer)

        for address in customer["addresses"]:
            bridge_customer_address_entity = BridgeCustomerAddressEntity()

            mapped_customer_address = bridge_customer_address_entity.map_sw6_to_db(customer=customer, address=address)

            mapped_customer.addresses.append(mapped_customer_address)

        return mapped_customer
