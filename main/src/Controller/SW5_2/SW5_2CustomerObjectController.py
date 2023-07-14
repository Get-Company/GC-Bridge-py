from datetime import datetime

from sqlalchemy import or_, and_

from main.src.Controller.SW5_2.SW5_2ObjectController import SW5_2ObjectController
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity
from main.src.Entity.SW5_2.SW5_2AddressObjectEntity import SW5_2AddressObjectEntity
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from pprint import pprint

from main import db


class SW5_2CustomerObjectController(SW5_2ObjectController):
    def __init__(self):

        super().__init__()

    def delete_duplicates_by_adrnr(self, adrnr):
        # get all the doubles
        double_customers = SW5_2CustomerObjectEntity().get_all_customers_by_adrnr(adrnr)
        print("Found", double_customers["total"], "doubles for", adrnr)
        double_customers_detail_list = []
        for customer in double_customers["data"]:

            double_customers_by_adrnr = SW5_2CustomerObjectEntity().get_customer(customer["id"])
            pprint(double_customers_by_adrnr)
            for dcba in double_customers_by_adrnr["data"]:
                pprint(dcba)
                double_customers_detail_list.append(dcba)

            double_customers_by_email = SW5_2CustomerObjectEntity().get_all_customers_by_email(customer["email"])
            print("Found", double_customers_by_email["total"], "doubles for", customer["email"])
            # for dcbe in double_customers_by_email["data"]:
            #     double_customer_by_email_detail = SW5_2CustomerObjectEntity().get_customer(dcbe["id"])
            #     double_customers_detail_list.append(double_customer_by_email_detail["data"])

        for cust in double_customers_detail_list:
            pprint(cust["id"])
        return True

    def sync_customer(self, customer):
        is_in_db = BridgeCustomerEntity().query.filter_by(api_id=customer["id"]).one_or_none()
        new_bridge_customer = BridgeCustomerEntity()
        new_bridge_customer.map_sw5_to_db(customer)

        if is_in_db:
            for_db = is_in_db.update_entity(new_bridge_customer)
            for_db.addresses = []
        else:
            for_db = new_bridge_customer

        db.session.add(for_db)

        for address in customer["addresses"]:
            self._sync_address(address=address)

        self.commit_with_errors()

        # Now set the shipping and billing addresses

        return True

    def _sync_address(self, address):
        is_in_db = BridgeCustomerAddressEntity().query.filter_by(api_id=address["id"]).one_or_none()
        sw5_address = SW5_2CustomerObjectEntity().get_addresses(address_id=address["id"])

        new_bridge_address = BridgeCustomerAddressEntity()
        new_bridge_address.map_sw5_to_db(address=sw5_address)

        if is_in_db:
            for_db = is_in_db.update_entity(new_bridge_address)
        else:
            for_db = new_bridge_address

        db.session.add(for_db)

    """
    Atti
    """

    def get_new_customer(self, data):
        customer = db.session.query(BridgeCustomerEntity).filter(
            (BridgeCustomerEntity.erp_nr == data['data']['number']) |
            (BridgeCustomerEntity.api_id == data['data']['id'])
        ).one_or_none()

        if customer:
            print("Existing customer found! Updating information.")
            customer.addresses = []

            created_at = datetime.strptime(data["data"]["firstLogin"], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
            updated_at = datetime.strptime(data["data"]["changed"], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)

            customer.email = data['data']['email']
            # Changed to NUll
            # customer.erp_ltz_aend = datetime.now()
            customer.updated_at = updated_at

            for address in data['data']['addresses']:
                erp_ansnr = 0
                if address['salutation'] == "ms":
                    salutation = "Frau"
                elif address['salutation'] == "mr":
                    salutation = "Herr"
                elif address['salutation'] == "company":
                    salutation = "Firma"

                existing_address = db.session.query(BridgeCustomerAddressEntity).filter_by(api_id=address['id']).first()
                if existing_address:
                    existing_address.first_name = address['firstname']
                    existing_address.last_name = address['lastname']
                    existing_address.str = address['street']
                    existing_address.plz = address['zipcode']
                    existing_address.city = address['city']
                    existing_address.email = data['data']['email']
                    existing_address.company = address['company']
                    # Changed to Null
                    # existing_address.erp_ltz_aend = datetime.now()
                    existing_address.updated_at = data["data"]["attribute"]["lastmodified"]
                else:
                    new_address = BridgeCustomerAddressEntity(
                        api_id=address['id'],
                        erp_nr=data['data']['number'],
                        # erp_ansnr=erp_ansnr,
                        # erp_aspnr=0,
                        na1=salutation,
                        title=salutation,
                        first_name=address['firstname'],
                        last_name=address['lastname'],
                        na2=address['lastname'],
                        str=address['street'],
                        plz=address['zipcode'],
                        city=address['city'],
                        email=data['data']['email'],
                        land_ISO2="DE",
                        company=address['company'],
                        erp_ltz_aend=datetime.now(),
                        created_at=created_at,
                        updated_at=updated_at,
                        customer_id=customer.id
                    )
                    db.session.add(new_address)

                if address['id'] == data['data']['defaultBillingAddress']['id']:
                    customer.erp_reansnr = erp_ansnr

                if address['id'] == data['data']['defaultShippingAddress']['id']:
                    customer.erp_liansnr = erp_ansnr

            db.session.commit()
            print(f"Customer updated ID: {data['data']['id']}")

        else:
            print(f"Creating new customer by ID:{data['data']['id']}")

            created_at = datetime.strptime(data["data"]["firstLogin"], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
            updated_at = datetime.strptime(data["data"]["changed"], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)

            new_customer = BridgeCustomerEntity(
                api_id=data['data']['id'],
                erp_nr=data['data']['number'],
                email=data['data']['email'],
                erp_reansnr=0,
                erp_liansnr=0,
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(new_customer)
            db.session.commit()

            erp_ansnr = 0
            for address in data['data']['addresses']:
                if address['salutation'] == "ms":
                    salutation = "Frau"
                elif address['salutation'] == "mr":
                    salutation = "Herr"
                elif address['salutation'] == "company":
                    salutation = "Firma"

                new_address = BridgeCustomerAddressEntity(
                    api_id=address['id'],
                    erp_nr=data['data']['number'],
                    erp_ansnr=erp_ansnr,
                    erp_aspnr=0,
                    na1=salutation,
                    title=salutation,
                    first_name=address['firstname'],
                    last_name=address['lastname'],
                    na2=address['lastname'],
                    str=address['street'],
                    plz=address['zipcode'],
                    city=address['city'],
                    email=data['data']['email'],
                    land_ISO2="DE",
                    company=address['company'],
                    created_at=created_at,
                    updated_at=updated_at,
                    customer_id=new_customer.id
                )
                db.session.add(new_address)

                if address['id'] == data['data']['defaultBillingAddress']['id']:
                    new_customer.erp_reansnr = erp_ansnr

                if address['id'] == data['data']['defaultShippingAddress']['id']:
                    new_customer.erp_liansnr = erp_ansnr

                erp_ansnr += 1

            db.session.commit()
            print(f"New customer added: {data['data']['id']}")

    """
    Flo 2.0
    """

    def upsert_customer(self, customer_data):
        """
        Search for a customer in the database and add them if they do not exist.

        Parameters:
            customer_data (dict): A dictionary that contains the customer data.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        mapped_bridge_customer = BridgeCustomerEntity().map_sw5_to_db(customer_data["data"])
        customer_in_db = None
        try:
            # Validate the extracted data
            if not mapped_bridge_customer.email or not mapped_bridge_customer.erp_nr:
                print("Invalid customer data.")
                return None

            # Search for the customer in the database
            customer_in_db = BridgeCustomerEntity.query.filter(
                or_(
                    BridgeCustomerEntity.email == mapped_bridge_customer.email,
                    BridgeCustomerEntity.erp_nr == mapped_bridge_customer.erp_nr
                )
            ).one_or_none()

        except Exception as e:
            print(f"Error processing customer data: {e}")
            return False

        if customer_in_db:
            customer_for_db = customer_in_db.update_entity(mapped_bridge_customer)
        else:
            customer_for_db = mapped_bridge_customer

        address_index = 0
        for address in customer_data["data"]["addresses"]:
            address_data = SW5_2AddressObjectEntity().get_address(address["id"])
            address = address_data["data"]
            mapped_bridge_address = BridgeCustomerAddressEntity().map_sw5_to_db(address)

            mapped_bridge_address.erp_ansnr = address_index
            mapped_bridge_address.erp_aspnr = 0
            address_index += 1
            customer_address_in_db = None
            try:
                # Validate the extracted data
                if not mapped_bridge_address.erp_nr or not mapped_bridge_address.api_id:
                    print("Invalid customer data.")
                    return None

                # Search the customer address in the database
                customer_address_in_db = BridgeCustomerAddressEntity.query.filter(
                    and_(
                        BridgeCustomerAddressEntity.erp_nr == mapped_bridge_address.erp_nr,
                        BridgeCustomerAddressEntity.api_id == mapped_bridge_address.api_id
                    )
                ).one_or_none()
            except Exception as e:
                print(f"Error processing customer address data: {e}")
                return False

            if customer_address_in_db:
                customer_address_for_db = customer_address_in_db.update_entity(mapped_bridge_address)
            else:
                customer_address_for_db = mapped_bridge_address

            customer_for_db.addresses.append(customer_address_for_db)

            # Set the standard billing and shipping address
            # if customer_data["data"]["defaultBillingAddress"] == address["id"]:
            #     customer_for_db.billing_address = customer_address_for_db
            # if customer_data["data"]["defaultShippingAddress"] == address["id"]:
            #     customer_for_db.shipping_address = customer_address_for_db

        customer_for_return = customer_for_db
        db.session.add(customer_for_db)

        self.commit_with_errors()

        return customer_for_return
