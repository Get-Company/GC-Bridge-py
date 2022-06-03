import datetime
import pytz

from .APIClient import *
from main.src.Controller.ERP.ERPController import *
from main.src.Entity.SW5.SW5CustomerEntity import SW5CustomerEntity

from main.src.Repository.functions_repository import parse_a_date


def sw5_sync_duplicates_v2(false_adrnr, right_adrnr):
    ###
    # 1. Create connection to ERP
    erp_connect('58')

    ###
    # 2. Make dict for false and right and create the object (get the dataset)
    right_customer = SW5CustomerEntity(right_adrnr)
    false_customer = SW5CustomerEntity(false_adrnr)

    ###
    # 3.1 Sync Webshop ID
    sync_webshop_id(right_customer=right_customer, false_customer=false_customer)

    # 3.2 Sync Amazon ID
    sync_amazon_id(right_customer=right_customer, false_customer=false_customer)

    ###
    # 4. Get Customer from SW5
    api = client_from_env()

    # # 4.1 Set the fields like last Login, password hash and password encoder etc... if the customer has a
    # # webshop ID = ShopAccount
    if right_customer.get_webshopid():
        right_customer = sync_fields_from_sw5(customer=right_customer, api=api)

    if false_customer.get_webshopid():
        false_customer = sync_fields_from_sw5(customer=false_customer, api=api)

    ###
    # 5 Set most recent last login, password and password encoder
    sync_last_login_fields_sw5(right_customer=right_customer, false_customer=false_customer, api=api)

    ###
    # 6. Get orders and change the customer from False to Right
    if false_customer.get_webshopid() and right_customer.get_orders_ids():
        right_customer.set_orders(api.get_order_by_customerId(false_customer.get_webshopid()))

    if right_customer.get_webshopid() and false_customer.get_orders_ids():
        right_customer.set_orders(api.get_order_by_customerId(right_customer.get_webshopid()))

    # 7 Set Addresses to right customer
    if right_customer.get_webshopid() and right_customer.get_addresses_ids():
        right_customer.set_addresses(api.get_address_by_userId(right_customer.get_webshopid()))

    if false_customer.get_webshopid() and false_customer.get_addresses_ids():
        right_customer.set_addresses(api.get_address_by_userId(false_customer.get_webshopid()))

    print(right_customer)
    print(false_customer)

    updated_right_customer = api.set_customer_addresses_orders_and_credentials(customer=right_customer)
    print("Updated Right Customer: ", updated_right_customer)

    # Delete false Customer from API
    # If we take the webshopid from false. Do not delete!
    if false_customer.get_webshopid() is not right_customer.get_webshopid():
        api.delete_customer_by_customerId(false_customer.get_webshopid())

    # Delete false_customer from erp
    false_customer.delete_erp_dataset_adresse()

    # Upload right customer to erp
    right_customer.set_erp_ids()

    # Close ERP Connection!!!!
    erp_close()


def sync_webshop_id(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity):
    """
    If right_customer has a webshop ID, keep it. If the right customer has none but false_customer has one. take it.
    If both have no webshop ID set it to False.
    :param right_customer: SW5CustomerEntity
    :param false_customer: SW5CustomerEntity
    :return: Boolean
    """
    # Case 1: right_customer has Webshop ID:
    if right_customer.get_webshopid():
        print("%s - Right customer has a Webshop ID. We keep it: %s \n" % (
            right_customer.get_adrnr(),
            right_customer.get_webshopid())
              )
        return True

    # Case 2 : right_customer has no Webshop ID. Has false_customer one?
    elif false_customer.get_webshopid():
        print("%s - False customer has a Webshop ID. We take it from there: %s\n" % (
            false_customer.get_adrnr(),
            false_customer.get_webshopid())
              )
        right_customer.set_webshopid(false_customer.get_webshopid())
        return True

    else:
        print("No Webshop ID found \n")
        right_customer.set_webshopid(False)
        return False


def sync_amazon_id(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity):
    """
        If right customer has an amazon ID, keep it. If the right customer has none but false customer has one. Take it.
        If both have no amazon ID set it to False.
        :param right_customer: SW5CustomerEntity
        :param false_customer: SW5CustomerEntity
        :return: Boolean
        """
    # Case 1: right_customer has Amazon ID:
    if right_customer.get_amazonid():
        print("%s - Right customer has a Amazon ID. We keep it: %s\n" % (
            right_customer.get_adrnr(),
            right_customer.get_amazonid())
              )
        return True

    # Case 2 : right_customer has no Amazon ID. Has false_customer one?
    elif false_customer.get_amazonid():
        print("%s - False customer has a Amazonp ID. We take it from there: %s\n" % (
            false_customer.get_adrnr(),
            false_customer.get_amazonid())
              )
        right_customer.set_amazonid(false_customer.get_amazonid())
        return True

    else:
        print("No Amazon ID found \n")
        right_customer.set_amazonid(False)
        return False


def sync_fields_from_sw5(customer: SW5CustomerEntity, api: APIClient):
    """
    Set some fields from SW5 to the customer. Does the right/false customer even have a webshop ID?
    :param customer: SW%CustomerEntity
    :param api:
    :return:
    """
    try:
        customer.set_fields_from_sw5(api.get_customer(customer.get_webshopid()))
        return customer
    except:
        # print("%s - No Customer with ID: %s in SW5 found" % (
        #     customer.get_adrnr(), customer.get_webshopid()))
        return customer


def sync_last_login_fields_sw5(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity, api: APIClient):
    """
    Get the most recent login date and set the password and password encoder to the right customer
    :param right_customer: object SW5CustomerEntity
    :param false_customer:  object SW5CustomerEntity
    :param api: object APIClient
    :return: Bool
    """
    older_date = datetime.datetime(1900, 1, 1, 10, 10, 10, 10, pytz.UTC)
    if right_customer.get_last_login():
        print("Right has lastlogn")
    else:
        print("Right hast no lastlogin, we set 01.01.1900")
        right_customer.set_last_login(older_date)

    if false_customer.get_last_login():
        print("False has lastlogin")
    else:
        print("False has no lastlogin, we set 01.01.1900")
        false_customer.set_last_login(older_date)

    if right_customer.get_last_login() > false_customer.get_last_login():
        print("Right was most recently logged in: %s > %s. We keep all fields!" % (
            right_customer.get_last_login(), false_customer.get_last_login()))
        return True
    else:
        print(
            "False was most recently logged in: %s < %s. We need to take the password and the encoder from false customer" % (
                right_customer.get_last_login(), false_customer.get_last_login()))
        # Set Customer fields in the SW5CustomerEntity
        right_customer.set_last_login(false_customer.get_last_login())
        right_customer.set_password_hash(false_customer.get_password_hash())
        right_customer.set_password_encoder(false_customer.get_password_encoder())
        right_customer.set_email(false_customer.get_email())
    return True


def sync_orders_sw5(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity, api: APIClient):
    """
    Get the orders for each customer and assign all the false customer orders to the right customer
    :param right_customer: object SW5CustomerEntity
    :param false_customer: object SW5CustomerEntity
    :param api: object APIClient
    :return: bool
    """
    # Get th orders
    right_customer.set_orders(api.get_order_by_customerId(right_customer.get_webshopid()))
    false_customer.set_orders(api.get_order_by_customerId(false_customer.get_webshopid()))

    # Now set every order of false customer to right customer
    for order in false_customer.get_orders():
        # print("Order Id: %s - CustomerId: %s -> CustomerId: %s" % (
        #     order['id'], order['customerId'], right_customer.get_webshopid()))
        api.set_order_customerId_by_orderId(right_customer.get_webshopid(), order['id'])

    # After setting all the orders in SW5, get them from the api and set them to the customer object
    # But first empty(clear) all orders, to avoid duplicates
    right_customer.unset_orders()
    right_customer.set_orders(api.get_order_by_customerId(right_customer.get_webshopid()))

    return True


def delete_erp_customer(customer: SW5CustomerEntity):
    customer.get_dataset_adresse().Edit()
    customer.get_dataset_adresse().Delete()
    customer.get_dataset_adresse().Post
    customer.get_dataset_adresse().Commit


def sync_erp_customer(customer: SW5CustomerEntity):
    customer.get_dataset_adresse().Edit()

    if customer.get_webshopid():
        customer.get_dataset_adresse().Fields("WShopAdrKz").AsBoolean = True
        customer.get_dataset_adresse().Fields("WShopID").AsString = customer.get_webshopid()
    else:
        customer.get_dataset_adresse().Fields("WShopAdrKz").AsBoolean = False
        customer.get_dataset_adresse().Fields("WShopID").AsString = ""

    if customer.get_amazonid():
        customer.get_dataset_adresse().Fields("AucWebKz").AsBoolean = True
        customer.get_dataset_adresse().Fields("AucWebID").AsString = customer.get_amazonid()
    else:
        customer.get_dataset_adresse().Fields("AucWebKz").AsBoolean = False
        customer.get_dataset_adresse().Fields("AucWebID").AsString = ""

    customer.get_dataset_adresse().Post
    customer.get_dataset_adresse().Commit
