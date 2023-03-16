from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import requests
import logging
from datetime import datetime, timedelta
from main.src.SW6_Bridge.config.config import config
from main.src.SW6_Bridge.log_exception import logger
from main.src.SW6_Bridge.modells.Customer import Customer, CustomerAddress
from main.src.SW6_Bridge.modells.Sync import Synchronize
from pprint import pprint
import pytz
import dateutil.parser
import time

engine = create_engine("mysql+pymysql://root:password@localhost:3306/gc-bridge_db")
Session = sessionmaker(bind=engine)
session = Session()

class SyncCustomers():
    def __init__(self):

        engine = create_engine("mysql+pymysql://root:password@localhost:3306/gc-bridge_db")
        Session = sessionmaker(bind=engine)
        session = Session()
        sw6_client_admin_url = config['sw_options']['shopware_admin_api_url']
        sw6_client_auth_url = config['sw_options']['shopware_auth_url']
        sw6_client_auth_params = {'grant_type': config['sw_options']['grant_type'],
                                  'client_id': config['sw_options']['client_id'],
                                  'client_secret': config['sw_options']['client_secret']}
        resp = requests.post(sw6_client_auth_url, data=sw6_client_auth_params).json()
        access_token = resp['access_token'] if 'access_token' in resp.keys() else None
        self.headers = {'Authorization': f'Bearer {access_token}','Content-Type': 'application/json'}
        self.base_url = config['sw_options']['shopware_admin_api_url']
        self.customer_endpoint = self.base_url + "/customer"
        print("Datebank connect.... OK OK OK OK OK!!!!!")

    def init_sync_BRIDGE_to_SW(self, customers):
        for customer in customers:
            payload = []
            addresses_payload = []
            for address in customer.addresses:
                addresses_payload.append({
                    'id': address.api_id,
                    'firstName': address.na1,
                    'lastName': address.na2,
                    'email': address.email,
                    'street': address.str,
                    'zipcode': address.plz,
                    'city': address.city,
                    'countryId': config['sw_options']['customers_params']['countryId'],
                    "salutationId": "1676fe16d2a9433c8239c33f671bba33"

                })

            payload.append({
                "id": customer.api_id,
                "customerNumber": customer.erp_nr,
                "groupId": "cfbd5018d38d41d8adca10d94fc8bdd6",
                "salesChannelId": "82216d6fa6744cfeb34197519656fcd7",
                "email": addresses_payload[0]['email'],
                "firstName": addresses_payload[0]['firstName'],
                "lastName": addresses_payload[0]['lastName'],
                "defaultPaymentMethodId": "f8e1b53a6f9141a1bc8805532dd6c4a0",
                "languageId": "513a4396f3f34edfa12d0e47f4b95d30",
                "defaultBillingAddress": addresses_payload[0],
                "defaultShippingAddress": addresses_payload[0],
                "addresses": addresses_payload[0:] if len(addresses_payload) > 0 else None,
                "updatedAt": str(datetime.now()),
                "salutationId": "1676fe16d2a9433c8239c33f671bba33"
            })

            data = json.dumps([
                {
                    "action": "upsert",
                    "entity": "customer",
                    "payload": payload
                }
            ], indent=4)

            try:
                print(payload)
                response = requests.post(f"http://localhost/api/_action/sync", headers=self.headers, data=data).json()
                print(response)
                logger.info(
                    f"Sw6Interface - sync_entity_to_sw - Uploading finished successfully - {len(response['data'][0]['result'])} data uploaded") \
                    if ((response['success'] == True) if 'success' in response.keys() else None) \
                    else logger.error(
                    f"Sw6Interface - sync_entity_to_sw - Problem occurred during uploading - {response['errors'] if 'errors' in response.keys() else response['data'][0]['result'][0]}")
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Sw6Interface - sync_entity_to_sw - Failed to upload all")
                raise SystemExit(e)


        print(f"3.{len(customers)} changed customer´s in BRIDGE is successfully uploaded!")

    def init_sync_SW_to_BRIDGE(self, customers):
        pass

    def upload_all_new_customer_from_shopware_to_bridge(self, config):
        print("#########################################################################")
        print("########## Upload all new customers from SHOPWARE ----> BRIDGE ##########")
        print("#########################################################################")
        time.sleep(2)
        print("1. Looking for new customers in Shopware...")
        time.sleep(2)
        sw6_client_admin_url = config['sw_options']['shopware_admin_api_url']
        sw6_client_auth_url = config['sw_options']['shopware_auth_url']
        sw6_client_auth_params = {'grant_type': config['sw_options']['grant_type'],
                                  'client_id': config['sw_options']['client_id'],
                                  'client_secret': config['sw_options']['client_secret']}
        resp = requests.post(sw6_client_auth_url, data=sw6_client_auth_params).json()
        access_token = resp['access_token'] if 'access_token' in resp.keys() else None
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

        url = sw6_client_admin_url + '/customer'
        response = requests.get(url, headers=headers)
        data = response.json()
        customer_ids = []

        for customer in data['data']:
            if 'attributes' in customer:
                customer_ids.append({"id": customer['id'],
                                     "name": customer['attributes']['firstName'] + ' ' + customer['attributes'][
                                         'lastName']})
            else:
                customer_ids.append({"id": customer['id'], "name": None})
        customer_ids = customer_ids

        existing_api_ids = [api_id[0] for api_id in session.query(Customer.api_id).all()]
        category_ids_set = set([category["id"] for category in customer_ids])
        existing_api_ids_set = set(existing_api_ids)
        new_api_ids = category_ids_set - existing_api_ids_set
        customer_data = []
        logger.info(f"New Customers found: {len(new_api_ids)}")
        for api_ids in new_api_ids:
            url = sw6_client_admin_url + f'/customer/{api_ids}'
            response = requests.get(url, headers=headers)
            customer = response.json()

            customer_info = customer['data']['attributes']
            first_name = customer_info['firstName']
            last_name = customer_info['lastName']
            email = customer_info['email']
            default_billing_address_id = customer_info['defaultBillingAddressId']
            default_shipping_address_id = customer_info['defaultShippingAddressId']

            url = sw6_client_admin_url + f'/customer/{api_ids}/addresses'
            response = requests.get(url, headers=headers)
            customer_addresses = response.json()

            addresses = []
            i = 0
            for data in customer_addresses['data']:
                addresses.append({
                })
                address = CustomerAddress(api_id=data['id'], erp_nr=data['id'], erp_ansnr=i, erp_aspnr=0,
                                          na1="Firma", na2=f"{first_name}",
                                          first_name=data['attributes']['firstName'],
                                          last_name=data['attributes']['lastName'],
                                          title="", email=email, str=data['attributes']['street'],
                                          plz=data['attributes']['zipcode'], city=data['attributes']['city'],
                                          land=276, land_ISO2="DE", company="Firma", erp_ltz_aend=datetime.now(),
                                          created_at=datetime.now(), updated_at=datetime.now())
                session.add(address)
                session.commit()
                i += 1

            customer_data.append({
                'customer_id': api_ids,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'addresses': addresses
            })

            db_customer = Customer(api_id=api_ids, erp_nr=api_ids, email=email, ustid=" ", erp_reansnr=0, erp_liansnr=0,
                                   created_at=datetime.now(), updated_at=datetime.now())
            for i, data in enumerate(customer_addresses['data']):
                if data["id"] == default_billing_address_id:
                    db_customer.erp_reansnr = i
                elif data["id"] == default_shipping_address_id:
                    db_customer.erp_liansnr = i
                session.add(db_customer)
                session.commit()
            for data in customer_addresses['data']:
                customer_addresses = session.query(CustomerAddress).filter_by(api_id=data['id']).first()
                customer_addresses.customer_id = db_customer.id
                session.add(customer_addresses)
                session.commit()
            session.add(customer_addresses)
            session.commit()
            print(f"2.{len(api_ids)} new customer´s from SHOPWARE ----> BRIDGE uploaded!")
            time.sleep(2)

    def sync_all_changed_customers_from_SW_to_bridge(self, config):

        print("#########################################################################")
        print("############# Sync all customers from SHOPWARE ----> BRIDGE #############")
        print("#########################################################################")
        time.sleep(2)
        print("1. Looking for changed customers in Shopware...")
        time.sleep(2)
        config = config
        sw6_client_admin_url = config['sw_options']['shopware_admin_api_url']
        sw6_client_auth_url = config['sw_options']['shopware_auth_url']
        sw6_client_auth_params = {'grant_type': config['sw_options']['grant_type'], 'client_id': config['sw_options']['client_id'], 'client_secret': config['sw_options']['client_secret']}
        resp = requests.post(sw6_client_auth_url, data=sw6_client_auth_params).json()
        access_token = resp['access_token'] if 'access_token' in resp.keys() else None
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        url = sw6_client_admin_url + '/customer'
        response = requests.get(url, headers=headers)
        data = response.json()

        engine = create_engine("mysql+pymysql://root:password@localhost:3306/gc-bridge_db")
        Session = sessionmaker(bind=engine)
        session = Session()

        update_list = []
        for customer in data['data']:
            customer_id = customer['id']
            customer_from_db = session.query(Customer).filter_by(api_id=customer_id).first()
            if customer_from_db:
                if customer['attributes']['updatedAt'] is None:
                    sw_updated_at = "2023-02-01 20:28:19"
                else:
                    sw_updated_at = dateutil.parser.parse(customer['attributes']['updatedAt'])
                    sw_updated_at = sw_updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    sw_updated_at = dateutil.parser.parse(sw_updated_at)
                if str(sw_updated_at) > str(customer_from_db.updated_at):
                    update_list.append(customer_id)



        customer_data = []
        if len(update_list) > 0:
            print(f"2. {len(update_list)} changed customers in Shopware found!")
            time.sleep(2)
            print(f"2. {len(update_list)} changed customers upload start...")
            for api_ids in update_list:
                url = sw6_client_admin_url + f'/customer/{api_ids}'
                response = requests.get(url, headers=headers)
                customer = response.json()

                customer_info = customer['data']['attributes']
                first_name = customer_info['firstName']
                last_name = customer_info['lastName']
                email = customer_info['email']
                default_billing_address_id = customer_info['defaultBillingAddressId']
                default_shipping_address_id = customer_info['defaultShippingAddressId']
                url = sw6_client_admin_url + f'/customer/{api_ids}/addresses'
                response = requests.get(url, headers=headers)
                customer_addresses = response.json()
                addresses = []
                i = 0
                customer = session.query(Customer).filter_by(api_id=api_ids).first()

                address_api_ids = [address.api_id for address in customer.addresses]


                addresses_ids = [data['id'] for data in customer_addresses['data']]
                # addresses_in_db = session.query(CustomerAddress).filter(CustomerAddress.api_id.in_(addresses_ids)).all()
                # addresses_api_ids_in_db = [address.api_id for address in addresses_in_db]

                for data in customer_addresses['data']:
                    address = session.query(CustomerAddress).filter_by(api_id=data['id']).first()
                    customer = session.query(Customer).filter_by(api_id=api_ids).first()

                    address_api_ids = [address.api_id for address in customer.addresses]

                    addresses_ids = [data['id'] for data in customer_addresses['data']]
                    addresses_in_db = session.query(CustomerAddress).filter(
                        CustomerAddress.api_id.in_(addresses_ids)).all()
                    addresses_api_ids_in_db = [address.api_id for address in addresses_in_db]
                    for address_api_id in address_api_ids:
                        if address_api_id not in addresses_api_ids_in_db:
                            session.query(CustomerAddress).filter_by(api_id=address_api_id).delete()
                            session.commit()
                            session.close()
                    if address:
                        # update existing address
                        address.first_name = data['attributes']['firstName']
                        address.last_name = data['attributes']['lastName']
                        address.email = email
                        address.str = data['attributes']['street']
                        address.plz = data['attributes']['zipcode']
                        address.city = data['attributes']['city']
                        address.updated_at = datetime.now()
                        session.add(address)
                        session.commit()
                        session.close()
                    else:
                        # create new address if not exists in database
                        address = CustomerAddress(
                            api_id=data['id'],
                            erp_nr=data['id'],
                            erp_ansnr=0,
                            erp_aspnr=0,
                            na1=" ",
                            na2=first_name + last_name,
                            first_name=data['attributes']['firstName'],
                            last_name=data['attributes']['lastName'],
                            title="",
                            email=email,
                            str=data['attributes']['street'],
                            plz=data['attributes']['zipcode'],
                            city=data['attributes']['city'],
                            land=276,
                            land_ISO2="DE",
                            company="Firma",
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                        )
                        session.add(address)
                        session.commit()
                    i += 1

                customer_data.append({
                    'customer_id': api_ids,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'addresses': addresses
                })
                #print(data)
                db_customer = session.query(Customer).filter_by(api_id=api_ids).first()
                db_customer.api_id = api_ids
                #db_customer.erp_nr = data['attributes']['customerNumber']
                db_customer.email = email
                #db_customer.ustid = " "
                db_customer.erp_reansnr = 0
                db_customer.erp_liansnr = 0
                db_customer.updated_at = datetime.now()
                session.add(db_customer)
                session.commit()
                session.close()
                #print(db_customer.email)
                for i, data in enumerate(customer_addresses['data']):
                    if data["id"] == default_billing_address_id:
                        db_customer.erp_reansnr = i
                    elif data["id"] == default_shipping_address_id:
                        db_customer.erp_liansnr = i
                    session.add(db_customer)
                    session.commit()
                for data in customer_addresses['data']:
                    customer_addresses = session.query(CustomerAddress).filter_by(api_id=data['id']).first()
                    customer_addresses.customer_id = db_customer.id
                    customer_addresses.na1 = "Firma"
                    session.add(customer_addresses)
                    session.commit()
                session.add(customer_addresses)
                session.commit()
            print(f"3. {len(update_list)} changed customers successful uploaded!")
            time.sleep(2)
            last_sync_sw6 = session.query(Synchronize).filter_by(id=1).first()
            last_sync_sw6.sw6_customers_sync_date = datetime.now()
            session.add(last_sync_sw6)
            session.commit()
            session.close()
        else:
            print(f"2. NO changed customers in Shopware found")
            time.sleep(2)
            last_sync_sw6 = session.query(Synchronize).filter_by(id=1).first()
            last_sync_sw6.sw6_customers_sync_date = datetime.now()
            session.add(last_sync_sw6)
            session.commit()
            session.close()

    def sync_all_changed_customers_from_BRIDGE_to_sw(self, config):

        print("#########################################################################")
        print("############# Sync all customers from BRIDGE ----> SHOPWARE #############")
        print("#########################################################################")
        time.sleep(2)
        print(f"1. Looking for changed customers in BRIDGE")
        time.sleep(2)
        sync = session.query(Synchronize).filter_by(id=1).first()
        last_sync_time_sw6 = sync.sw6_customers_sync_date
        customers = session.query(Customer).filter(Customer.updated_at > last_sync_time_sw6).all()
        api_ids = [api_id.api_id for api_id in customers]
        if len(customers) > 0:
            print(f"2.{len(api_ids)} changed customer´s in BRIDGE found!")
            time.sleep(2)
            print(f"3.{len(api_ids)} changed customer´s in BRIDGE upload start....")
            time.sleep(2)
            self.init_sync_BRIDGE_to_SW(customers)

            session.commit()

            session.close()
        else:

            session.close()

    # def sync_all_changed_customers_from_BRIDGE_to_sw(self, config):
    #
    #     print("#########################################################################")
    #     print("############# Sync all customers from BRIDGE ----> SHOPWARE #############")
    #     print("#########################################################################")
    #     time.sleep(2)
    #     print(f"1. Looking for changed customers in BRIDGE")
    #     time.sleep(2)
    #     sync = session.query(Synchronize).filter_by(id=1).first()
    #     last_sync_time_sw6 = sync.sw6_customers_sync_date
    #     customers = session.query(Customer).filter(Customer.updated_at > last_sync_time_sw6).all()
    #     api_ids = [api_id.api_id for api_id in customers]
    #     if len(customers) > 0:
    #         print(f"2.{len(api_ids)} changed customer´s in BRIDGE found!")
    #         time.sleep(2)
    #         print(f"3.{len(api_ids)} changed customer´s in BRIDGE upload start....")
    #         time.sleep(2)
    #         self.init_sync_BRIDGE_to_SW(customers)
    #         last_sync_sw6 = session.query(Synchronize).filter_by(id=1).first()
    #         last_sync_sw6.sw6_customers_sync_date = datetime.now()
    #         session.add(last_sync_sw6)
    #         session.commit()
    #
    #         session.close()
    #     else:
    #         last_sync_sw6 = session.query(Synchronize).filter_by(id=1).first()
    #         last_sync_sw6.sw6_customers_sync_date = datetime.now()
    #         session.add(last_sync_sw6)
    #         session.commit()
    #         session.close()


    def sync_selected_customers_from_BRIDGE_to_sw_WITH_SYNC_CHECK(self, config, start_range, end_range):
        sync = session.query(Synchronize).filter_by(id=1).first()
        last_sync_time_sw6 = sync.sw6_customers_sync_date
        customers = session.query(Customer).filter(Customer.updated_at > last_sync_time_sw6) \
            .filter(Customer.erp_nr >= start_range) \
            .filter(Customer.erp_nr <= end_range) \
            .all()
        api_ids = [api_id.api_id for api_id in customers]
        print(api_ids)
        self.init_sync_BRIDGE_to_SW(customers)

    def sync_selected_customers_from_BRIDGE_to_sw_WITHOUT_SYNC_CHECK_NIIIIX_CHECKEN_DIESE(self, start_range, end_range):
        customers = session.query(Customer).filter(Customer.erp_nr >= start_range) \
            .filter(Customer.erp_nr <= end_range) \
            .all()
        api_ids = [api_id.api_id for api_id in customers]
        print(api_ids)
        self.init_sync_BRIDGE_to_SW(customers)


sync = SyncCustomers()




