from typing import Union
from sqlalchemy.exc import IntegrityError, InvalidRequestError, SQLAlchemyError


from main.src.Controller.ERP.ERPController import ERPController
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

from main import db


class ERPCustomerController(ERPController):
    def __init__(self, erp_obj):
        self.erp_obj = erp_obj
        self.erp_entity = ERPAdressenEntity(erp_obj=erp_obj)
        self.erp_address_entity = ERPAnschriftenEntity(erp_obj=erp_obj)
        self.bridge_entity = BridgeCustomerEntity()
        self.webshop_filter = "WShopAdrKz = '1'"
        # Downsert
        self.new_or_updated_customers_in_bridge = None

        super().__init__(erp_obj)

    def sync_range_upsert(self, start, end, field=None):
        # 1. Get Customers from ERP
        self.erp_entity.set_range(start=start, end=end)
        self.erp_entity.filter_expression(self.webshop_filter)
        self.erp_entity.filter_set()
        self.erp_entity.range_first()

        self.upsert_customer()

    def sync_changed_upsert(self):
        # 1. What customers have changed in erp
        self.erp_entity.get_all_since_last_sync()

        self.upsert_customer()

    def sync_changed_downsert(self):
        bridge_synchronize = BridgeSynchronizeEntity().get_entity_by_id_1()
        last_sync = bridge_synchronize.dataset_address_sync_date
        self.new_or_updated_customers_in_bridge = BridgeCustomerEntity.query.filter(
            BridgeCustomerEntity.updated_at>=last_sync
        ).all()

        self.downsert_customer()

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

    def upsert_customer(self):
        # Loop through all the customers
        while not self.erp_entity.range_eof():
            is_in_db = self.is_customer_in_bridge(customer=self.erp_entity)

            if is_in_db:
                erp_date = self.erp_entity.get_("LtzAend").replace(tzinfo=None)
                bridge_date = is_in_db.updated_at.replace(tzinfo=None)
                if erp_date >= bridge_date:
                    print("Customer Update")
                    bridge_customer = BridgeCustomerEntity().map_erp_to_db(self.erp_entity)
                    is_in_db.update_entity(bridge_customer)
                    db.session.add(is_in_db)
                    self.commit_with_errors()
                    # Now all the addresses
                    self._upsert_addresses()
                else:
                    print("Customer Pass. Old.", self.erp_entity.get_("AdrNr"))
            else:
                bridge_customer = BridgeCustomerEntity().map_erp_to_db(erp_entity=self.erp_entity)
                db.session.add(bridge_customer)
                self.commit_with_errors()
                # Now all the addresses
                self._upsert_addresses()

            self.erp_entity.range_next()

        return True

    def _upsert_addresses(self):
        print("Upsert Address for:", self.erp_entity.get_("AdrNr"))

        bridge_customer = BridgeCustomerEntity().query.filter_by(erp_nr=self.erp_entity.get_("AdrNr")).one_or_none()

        anschriften = self.erp_entity.get_anschriften()
        while not anschriften.range_eof():
            ansprechpartner = anschriften.get_ansprechpartner()
            while not ansprechpartner.range_eof():

                # Map the fields
                mapped_bridge_address = BridgeCustomerAddressEntity().map_erp_to_db(
                    erp_address_entity=anschriften,
                    erp_contact_entity=ansprechpartner
                )

                # Find the entity in th db
                bridge_address = BridgeCustomerAddressEntity().query\
                    .filter_by(erp_nr=ansprechpartner.get_("AdrNr"))\
                    .filter_by(erp_ansnr=ansprechpartner.get_("AnsNr"))\
                    .filter_by(erp_aspnr=ansprechpartner.get_("AspNr"))\
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

            bridge_synchronize = BridgeSynchronizeEntity().get_entity_by_id_1()

        return True

    def downsert_customer(self):
        # for customer in self.new_or_updated_customers_in_bridge:
        #     erp_customer = ERPAdressenEntity(erp_obj=self.erp_obj, id_value=customer.erp_nr)
        #     print(erp_customer.get_("AdrNr"), "from ERP, ", erp_customer)
        # return True

        erp_customer = ERPAdressenEntity(erp_obj=self.erp_obj).find_(field="Nr", value=111111)
        if erp_customer:
            print("Customer found, Update")
        elif not erp_customer:
            print(
                "Customer not found, Insert with adrnr:",
                ERPAdressenEntity(erp_obj=self.erp_obj).get_next_free_adrnr()
            )
        return True


    def commit_with_errors(self):
        try:
            db.session.commit()
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