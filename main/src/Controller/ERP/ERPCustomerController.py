"""
Maßgeblich beteiligt war da Bauer Andi,
der wo rausgefunden hat, dass es besser wäre, wenn das letzte
Sync-Datum vom einen auf den andern übertragen wird!!!
02.02.2023
"""

from typing import Union
from sqlalchemy.exc import IntegrityError, InvalidRequestError, SQLAlchemyError

from main.src.Controller.ERP.ERPController import ERPController
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

from main import db
from pprint import pprint
from datetime import datetime
import time


class ERPCustomerController(ERPController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj
        self.erp_entity = ERPAdressenEntity(erp_obj=erp_obj)
        self.erp_address_entity = ERPAnschriftenEntity(erp_obj=erp_obj)
        self.bridge_entity = BridgeCustomerEntity()
        self.webshop_filter = "WShopAdrKz = '1'"

        self.last_sync_date = BridgeSynchronizeEntity().get_dataset_customers_sync_date()

        # Downsert
        self.new_or_updated_customers_in_bridge = None

        super().__init__(erp_obj)

    """ #### Type of Sync #### """
    def sync_ranged(self, start, end):
        print("Customer Range Sync started", start, end)
        self.erp_entity.set_range(
            start=start, end=end
        )
        bridge_customer_list = self._get_ranged_bridge(start=start, end=end)

        self._sync(bridge_customer_list=bridge_customer_list)
        return True

    def _get_ranged_bridge(self, start, end):
        bridge_customers = BridgeCustomerEntity.query.filter(BridgeCustomerEntity.erp_nr.between(start, end)).all()

        return bridge_customers

    def sync_changed(self):
        print("Customer Changed Sync started", self.last_sync_date)
        # Get new or updated from both sides
        self.erp_entity.get_all_since_last_sync(last_sync_date=self.last_sync_date)
        bridge_customer_list = self._get_changed_bridge()

        self._sync(bridge_customer_list=bridge_customer_list)

        return True

    def _get_changed_bridge(self):
        bridge_synchronize = BridgeSynchronizeEntity().get_entity_by_id_1()
        customers = BridgeCustomerEntity.query.filter(
            BridgeCustomerEntity.updated_at >= self.last_sync_date
        ).all()

        return customers

    """ #### The sync Workload #### """
    def _sync(self, bridge_customer_list):
        bridge_synchronise_entity = BridgeSynchronizeEntity()
        self.last_sync_date = bridge_synchronise_entity.get_entity_by_id_1().dataset_customers_sync_date

        self.erp_entity.filter_expression(self.webshop_filter)
        self.erp_entity.filter_set()

        if self.erp_entity.range_count() >= 1:
            # 1 Sync ERP->Bridge
            print("###\n", "ERP->Bridge")
            print("###\n")
            self._sync_erp_customer_to_bridge()
        else:
            print("No new or updated Customer in ERP")

        if len(bridge_customer_list) >= 1:
            # 2 Sync Bridge->ERP
            print("###\n", "Bridge->ERP")
            print("###\n")
            self._sync_bridge_customer_to_erp(bridge_customer_list=bridge_customer_list)
        else:
            print("No new or updated Customer in Bridge")

        # Last set the sync date
        self.set_sync_date_now()

    """ #### ERP ---> Bridge #### """
    def _sync_erp_customer_to_bridge(self):
        """
        Check
            erp_date    >=  bridge_date
            LtzAend     >=  updated_at

        After that:
        bridge_synchronize_entity.dataset_customers_sync_date is set
        """
        # Don't set the date here, when downserting afterwrds. You will get a loop
        # self.set_sync_date_now()
        # Loop through all the customers
        while not self.erp_entity.range_eof():
            if not self.erp_entity.get_login():
                print("Customer ERP no E-Mail:", self.erp_entity.get_("AdrNr"))
                self.erp_entity.range_next()
                pass
            is_in_db = self.is_customer_in_bridge(customer=self.erp_entity)
            # Is the customer in the db
            if is_in_db:
                erp_date = self.erp_entity.get_("LtzAend").replace(tzinfo=None)
                bridge_date = is_in_db.updated_at.replace(tzinfo=None)
                # Is the customer newer than the db
                if erp_date >= bridge_date:
                    bridge_customer = BridgeCustomerEntity().map_erp_to_db(self.erp_entity)
                    is_in_db.update_entity(bridge_customer)
                    is_in_db.updated_at = self.erp_entity.get_("LtzAend")
                    print("Bridge Customer Update:", is_in_db.erp_nr, self.erp_entity.get_("LtzAend"), is_in_db.updated_at)
                    db.session.add(is_in_db)
                    # Is commit returning True
                    if self.commit_with_errors():
                        # Now all the addresses
                        self._sync_erp_customer_addresses_to_bridge(bridge_customer=is_in_db)
                        pass

                # Is the customer older than the db
                else:
                    pass

            # Customer is new?
            else:
                bridge_customer = BridgeCustomerEntity().map_erp_to_db(erp_entity=self.erp_entity)
                bridge_customer.updated_at = self.erp_entity.get_("LtzAend")
                print("Bridge Customer Create:", bridge_customer.erp_nr, self.erp_entity.get_("LtzAend"), bridge_customer.updated_at)
                db.session.add(bridge_customer)
                self.commit_with_errors()
                # Now all the addresses
                self._sync_erp_customer_addresses_to_bridge(bridge_customer=bridge_customer)

            self.erp_entity.range_next()
        return True

    def _sync_erp_customer_addresses_to_bridge(self, bridge_customer):
        bridge_customer.addresses = []
        db.session.add(bridge_customer)
        self.commit_with_errors()

        anschriften = self.erp_entity.get_anschriften()
        while not anschriften.range_eof():
            ansprechpartner = anschriften.get_ansprechpartner()
            while not ansprechpartner.range_eof():
                print("Search Anspr:",
                      ansprechpartner.get_("AdrNr"),
                      ansprechpartner.get_("AnsNr"),
                      ansprechpartner.get_("AspNr")
                      )
                # Map the fields
                mapped_bridge_address = BridgeCustomerAddressEntity().map_erp_to_db(
                    erp_address_entity=anschriften,
                    erp_contact_entity=ansprechpartner
                )

                # Find the entity in th db
                bridge_address = BridgeCustomerAddressEntity().query \
                    .filter_by(erp_nr=ansprechpartner.get_("AdrNr")) \
                    .filter_by(erp_ansnr=ansprechpartner.get_("AnsNr")) \
                    .filter_by(erp_aspnr=ansprechpartner.get_("AspNr")) \
                    .one_or_none()

                # If in db
                if bridge_address:
                    bridge_address.update_entity(mapped_bridge_address)
                    bridge_address.customer = bridge_customer
                    db.session.add(bridge_address)
                    self.commit_with_errors()

                else:
                    mapped_bridge_address.customer = bridge_customer
                    db.session.add(mapped_bridge_address)
                    self.commit_with_errors()

                ansprechpartner.range_next()
            anschriften.range_next()

        return True

    """ #### Bridge ---> ERP #### """
    def _sync_bridge_customer_to_erp(self, bridge_customer_list):
        """
        :return:
        """
        for bridge_customer in bridge_customer_list:
            erp_customer = ERPAdressenEntity(erp_obj=self.erp_obj, id_value=bridge_customer.erp_nr)
            # Customer
            if erp_customer:
                erp_customer.update_customer(update_fields_list=bridge_customer.map_db_to_erp())
                print("ERP Customer Update:", erp_customer.get_("AdrNr"), bridge_customer.updated_at, erp_customer.get_("LtzAend"))
                # Adresses
                for bridge_address in bridge_customer.addresses:
                    erp_address = ERPAnschriftenEntity(erp_obj=self.erp_obj, id_value=[
                        bridge_customer.erp_nr,
                        bridge_address.erp_ansnr
                    ])
                    if erp_address:
                        pass
                        # print(erp_address.get_("Na1"), erp_address.get_("Na2"), erp_address.get_("Na3"))
                    else:
                        pass
            else:
                pass
                # Todo Create Customer
                print("Create new Customer")
                # new_customer = ERPAdressenEntity(erp_obj=self.erp_obj)
                # new_customer.create_new_customer()
            # Addesses

        return True

    def set_sync_date_now(self):
        print("Set Last Sync Date")
        bridge_synchronize_entity = BridgeSynchronizeEntity()
        BridgeSynchronizeEntity().set_dataset_customers_sync_date(datetime.now())
        db.session.add(bridge_synchronize_entity)
        self.commit_with_errors()
        return True

    def commit_with_errors(self):
        try:
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            print("Error: Integrity constraint violated.")
            print(e)
        except InvalidRequestError:
            db.session.rollback()
            print("Error: Invalid request.")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error: {e}")

################################ ALT #########################
    """
    Upsert = ERP -> Bridge 
    """
    def sync_range_upsert(self, start, end, field=None):
        # 1. Get Customers from ERP
        self.erp_entity.set_range(start=start, end=end)
        self.erp_entity.filter_expression(self.webshop_filter)
        self.erp_entity.filter_set()
        self.erp_entity.range_first()

        self._upsert_customer()

    def sync_changed_upsert(self):
        self.erp_entity.get_all_since_last_sync()

        self._upsert_customer()

    """
    Downsert = Bridge -> ERP
    """
    def sync_changed_downsert(self):
        bridge_synchronize = BridgeSynchronizeEntity().get_entity_by_id_1()
        last_sync = bridge_synchronize.dataset_customers_sync_date
        customers = BridgeCustomerEntity.query.filter(
            BridgeCustomerEntity.updated_at >= last_sync
        ).all()

        if customers:
            self.new_or_updated_customers_in_bridge = customers
            self._downsert_customer()
        else:
            print("No new customer found in bridge")
            return True


    """
    Sync Tools
    """

    def is_customer_in_bridge(self, customer: ERPAdressenEntity) -> Union[ERPAdressenEntity, Exception]:
        """
        Check if a given ERPAdressenEntity is present in the bridge table.
        :param customer: The ERPAdressenEntity to check for in the bridge table.
        :type customer: ERPAdressenEntity
        :return: The customer object if it is present in the bridge table, None otherwise.
        :rtype: Union[ERPAdressenEntity, Exception]
        """
        customer_number = customer.get_("AdrNr")
        res = self.bridge_entity.query.filter_by(erp_nr=customer_number).one_or_none()
        if res:
            return res
        elif not res:
            return None
        else:
            raise Exception("Multiple Entries found")


