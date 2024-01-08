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
from datetime import datetime, timedelta
import time

from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity


class ERPCustomerController(ERPController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj
        self.erp_entity = ERPAdressenEntity(erp_obj=erp_obj)
        self.erp_address_entity = ERPAnschriftenEntity(erp_obj=erp_obj)
        self.bridge_entity = BridgeCustomerEntity()
        self.webshop_filter = "WShopAdrKz = '1'"

        self.last_sync_date = BridgeSynchronizeEntity().get_dataset_customers_sync_date()

        self.bridge_customer_list = []

        super().__init__(erp_obj)

    """ #### Type of Sync #### """

    def sync_ranged(self, start, end):
        print("Customer Range Sync started", start, end)
        erp_customer_found = self.erp_entity.set_range(
            start=start, end=end
        )
        if not erp_customer_found:
            self.erp_entity = None

        self.bridge_customer_list = self._get_ranged_bridge(start=start, end=end)
        self._sync()
        return True

    def _get_ranged_bridge(self, start, end):
        bridge_customers = BridgeCustomerEntity.query.filter(BridgeCustomerEntity.erp_nr.between(start, end)).all()

        return bridge_customers

    def sync_changed(self):
        # Get new or updated from both sides
        # erp_customer_found = self.erp_entity.get_all_since_last_sync(last_sync_date=self.last_sync_date, offset=1)
        # if erp_customer_found:
        #     while not self.erp_entity.range_eof():
        #         print("ERP Customer found:", self.erp_entity.get_("AdrNr"), self.erp_entity.get_("LtzAend"))
        #         self.erp_entity.range_next()
        # else:
        #     self.erp_entity = None
        #     print("No ERP Customer found.")

        self.bridge_customer_list = self._get_changed_bridge()
        if self.bridge_customer_list:
            for customer in self.bridge_customer_list:
                print("Bridge Customer found:", customer.erp_nr)
        else:
            print("No new customer in Bridge")

        # Last set the sync date
        # self.set_sync_date_now()

        self._sync()

        return True

    def _get_changed_bridge(self):
        customers = BridgeCustomerEntity.query.filter(
            BridgeCustomerEntity.updated_at >= self.last_sync_date
        ).all()

        return customers

    """ #### The sync Workload #### """

    def _sync(self):
        # Do we have results?
        # print("ERP Entity", self.erp_entity)
        # if self.erp_entity is not None:
        #
        #     self.erp_entity.filter_expression(self.webshop_filter)
        #     self.erp_entity.filter_set()
        #
        #     # 1 Sync ERP->Bridge
        #     print("\n###\n", "ERP->Bridge")
        #     print("###\n")
        #     # self._sync_erp_customer_to_bridge()
        # else:
        #     print("No new or updated Customer in ERP")

        if len(self.bridge_customer_list) >= 1:
            # 2 Sync Bridge->ERP
            print("###\n", "Bridge->ERP")
            print("###\n")
            self._sync_bridge_customers_to_erp()
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
        self.erp_entity.range_first()
        while not self.erp_entity.range_eof():
            # Is the customer in the db

            is_in_db = self.is_customer_in_bridge(customer=self.erp_entity)
            if is_in_db:
                print("Yes, in db:", is_in_db.id)
                erp_date = self.erp_entity.get_("LtzAend").replace(tzinfo=None)
                bridge_date = is_in_db.updated_at.replace(tzinfo=None)

                # Is erp newer than the db
                if erp_date > bridge_date:
                    bridge_customer = BridgeCustomerEntity().map_erp_to_db(self.erp_entity)

                    if not bridge_customer:
                        print("Passing Customer")
                        self.erp_entity.range_next()

                    is_in_db.update_entity(bridge_customer)
                    print("Buchner Felder jetzt:", is_in_db.id, is_in_db.api_id, is_in_db.erp_nr, erp_date,
                          is_in_db.updated_at)
                    db.session.add(is_in_db)
                    # Is commit returning True
                    if self.commit_with_errors():
                        # Das aktualisierte Objekt aus der Datenbank abrufen
                        updated_bridge_customer = self.bridge_entity.query.filter_by(id=is_in_db.id).one_or_none()

                        # Überprüfen, ob das Objekt korrekt aktualisiert wurde
                        if updated_bridge_customer:
                            print("Das aktualisierte Objekt wurde erfolgreich aus der Datenbank abgerufen.")
                        else:
                            print("Es gab ein Problem beim Abrufen des aktualisierten Objekts aus der Datenbank.")

                        # Now all the addresses
                        self._sync_erp_customer_addresses_to_bridge(bridge_customer=updated_bridge_customer)

                # Is the customer older than the db
                else:
                    print("Erp is not newer than bridge")


            # Customer is new?
            else:
                print("No, not in db!")
                bridge_customer = BridgeCustomerEntity().map_erp_to_db(erp_entity=self.erp_entity)
                bridge_customer.updated_at = self.erp_entity.get_("LtzAend")
                bridge_customer.updated_at = bridge_customer.updated_at + timedelta(seconds=1)
                print("Bridge Customer Create:", bridge_customer.erp_nr, self.erp_entity.get_("LtzAend"),
                      bridge_customer.updated_at)
                db.session.add(bridge_customer)
                if self.commit_with_errors():
                    # Now all the addresses
                    self._sync_erp_customer_addresses_to_bridge(bridge_customer=bridge_customer)

                else:
                    print("Address Commit gone Wrong", bridge_customer.erp_nr, bridge_customer.id)


            # Check if we are at the end of the range
            if self.erp_entity.range_eof():
                print("The last Customer")
                break
            else:
                print("Next customer")
                self.erp_entity.range_next()

        return True

    def _sync_erp_customer_addresses_to_bridge(self, bridge_customer):
        # Delete all related address to this customer
        for address in bridge_customer.addresses:
            db.session.delete(address)
        self.commit_with_errors()

        # Get Anschriften
        anschriften = self.erp_entity.get_anschriften()

        # Check if we got anschriften or return none
        if not anschriften:
            print("No Anschriften found.")
            return None

        print("We have", anschriften.range_count(), "anschriften")

        # Set the index for the anschriften while loop
        ans_index = 0

        # Start while Anschriften
        while not anschriften.range_eof():

            # Install a limit off synchronized anschriften
            if ans_index >= 999:
                break

            # get ansprechpartner
            ansprechpartner = anschriften.get_ansprechpartner()

            # Check if we got ansprechpartner or return none
            if not ansprechpartner:
                print("No Ansprechpartner found.")
                return None

            # Set the index for the ansprechpartner while loop
            ansp_index = 0

            # Start while Ansprechpartner
            while not ansprechpartner.range_eof():

                # Install a limit off synchronized ansprechpartner
                if ansp_index >= 50:
                    break

                # Do a print of the current Ansprechpartner
                print("Search Anspr:",
                      "AdrNr:",
                      ansprechpartner.get_("AdrNr"),
                      "AnsNr:",
                      ansprechpartner.get_("AnsNr"),
                      "AspNr:",
                      ansprechpartner.get_("AspNr"),
                      "AnsIndex:",
                      ans_index,
                      "AnspIndex:",
                      ansp_index,
                      )

                # Map the fields
                mapped_bridge_address = BridgeCustomerAddressEntity().map_erp_to_db(
                    erp_address_entity=anschriften,
                    erp_contact_entity=ansprechpartner
                )

                # Add the customer to the addresses
                mapped_bridge_address.customer = bridge_customer

                # Add and Commit the Address
                db.session.add(mapped_bridge_address)
                self.commit_with_errors()

                # Raise index by 1
                ansp_index += 1

                # End while if last ansprechpartner
                if ansprechpartner.range_eof():
                    print("End of range Asp")
                    break
                else:
                    print("Next Ansprechpartner")
                    ansprechpartner.range_next()

            # Raise Anschriften by 1
            ans_index += 1

            # End while if last anschrift
            if anschriften.range_eof():
                print("End of range Ans")
                break
            else:
                anschriften.range_next()

        return True

    """ #### Bridge ---> ERP #### """

    def _sync_single_bridge_customer_to_erp(self, bridge_customer):
        self.bridge_customer_list.append(bridge_customer)
        self._sync_bridge_customers_to_erp()

    def _sync_bridge_customers_to_erp(self):
        """
        :return:
        """
        for bridge_customer in self.bridge_customer_list:
            self.sync_bridge_customer_to_erp(bridge_customer=bridge_customer)

        return True

    def sync_bridge_customer_to_erp(self, bridge_customer):
        # Atti is setting the api_id 36 char into the erp_nr field
        # when the customer is new.
        if len(bridge_customer.erp_nr) > 5:
            erp_customer = None
        else:
            erp_customer = ERPAdressenEntity(erp_obj=self.erp_obj, id_value=bridge_customer.erp_nr)
            if bridge_customer.erp_nr != erp_customer.get_("AdrNr"):
                erp_customer = None
        # Customer Update
        if erp_customer:
            bridge_date = bridge_customer.updated_at
            erp_date = erp_customer.get_('LtzAend').replace(tzinfo=None)
            # If Bridge is newer
            if bridge_date > erp_date:
                # Adresses
                for bridge_address in bridge_customer.addresses:
                    self._sync_bridge_customer_addresses_to_erp(bridge_address=bridge_address)

                # Customer
                updated_fields_list = bridge_customer.map_db_to_erp()
                erp_customer.update_customer(
                    update_fields_list=updated_fields_list,
                    bridge_customer=bridge_customer
                )
                return erp_customer.get_("AdrNr")
            # Else Bridge is not newer, pass
            else:
                pass
            return erp_customer.get_("AdrNr")

        # New Customer, Create
        else:
            print("Create new Customer")
            new_customer = ERPAdressenEntity(erp_obj=self.erp_obj)

            customer_file = "webshop.yaml"
            default_billing_address = bridge_customer.get_default_billing_address()
            if default_billing_address.land_ISO2 and default_billing_address.land_ISO2 == "CH":
                customer_file = f"webshop_ch.yaml"
            try:
                new_customer_info = new_customer.create_new_customer(
                    bridge_customer=bridge_customer,
                    customer_file=customer_file
                )
            except Exception as e:
                print(e)

            if new_customer_info["adrnr"]:
                print(f"New Customer in ERP created!")

                bridge_customer.erp_nr = new_customer_info["adrnr"]
                for address in bridge_customer.addresses:
                    address.erp_nr = new_customer_info["adrnr"]
                    address.erp_ltz_aend = new_customer_info["erp_ltz_aend"]
                bridge_customer.erp_ltz_aend = new_customer_info["erp_ltz_aend"]
                db.session.add(bridge_customer)
                self.commit_with_errors()

                # Now lets forward the new adrnr to the shop
                # but only if it is not already there

                # get the customer again from the bridge
                in_db = BridgeCustomerEntity().query.filter_by(erp_nr=new_customer_info["adrnr"]).one_or_none()
                if in_db:
                    # Synch the new adrnr to shopware
                    adrn_in_sw5 = SW5_2CustomerObjectEntity().get_customer(
                        customer_id=new_customer_info["adrnr"],
                        is_number_not_id=True)
                    if adrn_in_sw5['success']:
                        print(f'AdrNr {new_customer_info["adrnr"]} existiert bereits in der DB')
                    else:
                        response = SW5_2CustomerObjectEntity().set_customer_number_by_id(customer_id=in_db.api_id,number=new_customer_info["adrnr"])

                return True
            else:
                print("New Customer was not created!", new_customer_info)
                return new_customer_info

    def _sync_bridge_customer_addresses_to_erp(self, bridge_address: BridgeCustomerAddressEntity):
        return
        erp_address = ERPAnschriftenEntity(erp_obj=self.erp_obj, id_value=[
            bridge_address.erp_nr,
            bridge_address.erp_ansnr
        ])
        # Is in db
        if erp_address:
            updated_fields_list = bridge_address.map_db_to_erp_anschrift()
            erp_address.update_address(update_fields_list=updated_fields_list)
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
            erp_contact.create_new_contact(adrnr=bridge_address.erp_nr, ansnr=bridge_address.erp_ansnr,
                                           aspnnr=bridge_address.erp_aspnr)

    def set_sync_date_now(self):
        """
        Sets the BridgeSynchronizeEntity dataset_customers_sync_date.
        """
        # datetime
        last_sync_date = datetime.now()

        # Set the dataset_customers_sync_date in BridgeSynchronizeEntity
        dataset_customers_sync_date = BridgeSynchronizeEntity().set_dataset_customers_sync_date(last_sync_date)
        db.session.add(dataset_customers_sync_date)

        # Commit changes to database
        self.commit_with_errors()

        return True

    def commit_with_errors(self):
        try:
            db.session.commit()
            print("\nCommit done")
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

    def is_customer_in_bridge(self, customer: ERPAdressenEntity) -> Union[BridgeCustomerEntity, Exception]:
        """
        Check if a given ERPAdressenEntity is present in the bridge table.
        :param customer: The ERPAdressenEntity to check for in the bridge table.
        :type customer: ERPAdressenEntity
        :return: The customer object if it is present in the bridge table, None otherwise.
        :rtype: Union[ERPAdressenEntity, Exception]
        """
        customer_number = customer.get_("AdrNr")
        print("Searching for", customer_number)
        res = self.bridge_entity.query.filter_by(erp_nr=customer_number).one_or_none()
        if res:
            return res
        elif not res:
            return None
        else:
            raise Exception("Multiple Entries found")
