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
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

from main import db
from pprint import pprint
from datetime import datetime
import time
import pytz


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
        # Get new or updated from both sides
        self.erp_entity.get_all_since_last_sync(last_sync_date=self.last_sync_date)
        bridge_customer_list = self._get_changed_bridge()

        # Last set the sync date
        self.set_sync_date_now()

        self._sync(bridge_customer_list=bridge_customer_list)

        return True

    def _get_changed_bridge(self):
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

    """ #### ERP ---> Bridge #### """
    def _sync_erp_customer_to_bridge(self):
        """
        Check
            erp_date    >=  bridge_date
            LtzAend     >=  updated_at

        After that:
        bridge_synchronize_entity.dataset_customers_sync_date is set
        """
        # Loop through all the customers
        while not self.erp_entity.range_eof():

            # Is the customer in the db
            is_in_db = self.is_customer_in_bridge(customer=self.erp_entity)
            if is_in_db:
                erp_date = self.erp_entity.get_("LtzAend").replace(tzinfo=None)
                bridge_date = is_in_db.updated_at.replace(tzinfo=None)

                # Is the customer newer than the db
                if erp_date > bridge_date:
                    bridge_customer = BridgeCustomerEntity().map_erp_to_db(self.erp_entity)

                    if not bridge_customer:
                        print("Passing Customer")
                        self.erp_entity.range_next()
                        continue

                    is_in_db.update_entity(bridge_customer)
                    is_in_db.updated_at = erp_date
                    print("Bridge Customer Update:", is_in_db.erp_nr, erp_date, is_in_db.updated_at)
                    db.session.add(is_in_db)
                    # Is commit returning True
                    if self.commit_with_errors():
                        # Now all the addresses
                        self._sync_erp_customer_addresses_to_bridge(bridge_customer=is_in_db)

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
        ans_index = 0
        ansp_index = 0
        while not anschriften.range_eof():
            if ans_index >= 200:
                break
            ansprechpartner = anschriften.get_ansprechpartner()
            while not ansprechpartner.range_eof():
                if ansp_index >= 100:
                    break
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
                ansp_index += 1
                ansprechpartner.range_next()
            ans_index += 1
            anschriften.range_next()

        return True

    """ #### Bridge ---> ERP #### """
    def _sync_bridge_customer_to_erp(self, bridge_customer_list):
        """
        :return:
        """
        for bridge_customer in bridge_customer_list:
            # Atti is setting the api_id 36 char into the erp_nr field
            # when the customer is new.
            if len(bridge_customer.erp_nr) == 5:
                erp_customer = ERPAdressenEntity(erp_obj=self.erp_obj, id_value=bridge_customer.erp_nr)
            else:
                erp_customer = False

            # Customer
            if erp_customer:
                bridge_date = bridge_customer.updated_at
                erp_date = erp_customer.get_('LtzAend').replace(tzinfo=None)
                # If Bridge is newer
                if bridge_date > erp_date:
                    erp_customer.update_customer(update_fields_list=bridge_customer.map_db_to_erp())
                    print("ERP Customer Update:", erp_customer.get_("AdrNr"), bridge_date, erp_date)
                    # Adresses
                    for bridge_address in bridge_customer.addresses:
                        print("Update Addresses")
                        self._sync_bridge_customer_addresses_to_erp(bridge_address=bridge_address)
                # Else Bridge is not newer, pass
                else:
                    pass
            # New Customer, Create
            else:
                print("Create new Customer")

                new_customer = ERPAdressenEntity(erp_obj=self.erp_obj)
                new_customer_info = new_customer.create_new_customer(bridge_customer=bridge_customer, customer_file='webshop.yaml')

                if new_customer_info["adrnr"]:
                    print(f"New Customer in ERP created!")
                    bridge_customer.erp_nr = new_customer_info["adrnr"]
                    for address in bridge_customer.addresses:
                        address.erp_nr = new_customer_info["adrnr"]
                        address.erp_ltz_aend = new_customer_info["erp_ltz_aend"]
                    bridge_customer.erp_ltz_aend = new_customer_info["erp_ltz_aend"]
                    db.session.add(bridge_customer)
                    self.commit_with_errors()
                else:
                    print("New Customer was not created!", new_customer)

        return True

    def _sync_bridge_customer_addresses_to_erp(self, bridge_address:BridgeCustomerAddressEntity):
        erp_address = ERPAnschriftenEntity(erp_obj=self.erp_obj, id_value=[
            bridge_address.erp_nr,
            bridge_address.erp_ansnr
        ])
        # Is in db
        if erp_address:
            erp_address.update_address(update_fields_list=bridge_address.map_db_to_erp_anschrift())
        else:
            erp_address.create_new_address(adrnr=bridge_address.erp_nr, ansnr=bridge_address.erp_ansnr)

        erp_contact = ERPAnsprechpartnerEntity(erp_obj=self.erp_obj, id_value=[
            bridge_address.erp_nr,
            bridge_address.erp_ansnr,
            bridge_address.erp_aspnr
        ])

        # Is in db
        if erp_contact:
            erp_contact.update_contact(update_fields_list=bridge_address.map_db_to_erp_ansprechpartner())
        else:
            erp_contact.create_new_contact(adrnr=bridge_address.erp_nr, ansnr=bridge_address.erp_ansnr, aspnnr=bridge_address.erp_aspnr)



    def set_sync_date_now(self):
        print("Set Last Sync Date")
        dataset_customers_sync_date = BridgeSynchronizeEntity().set_dataset_customers_sync_date(datetime.now())
        print(dataset_customers_sync_date)
        db.session.add(dataset_customers_sync_date)
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

        self._sync_erp_customer_to_bridge()

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

    def set_timezone(self, date, timezone="Europe/Berlin"):
        """Sets the timezone of a datetime object.

        Args:
            date (datetime): The datetime object to be modified.
            timezone (str, optional): The timezone to be set. Defaults to 'Europe/Berlin'.

        Returns:
            datetime: The datetime object with the specified timezone.
        """
        if date.tzinfo is None:
            date = pytz.utc.localize(date)

        return date.astimezone(pytz.timezone(timezone))
