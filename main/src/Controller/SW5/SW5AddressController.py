import datetime
import pytz

from .APIClient import *
from main.src.Controller.ERP.ERPController import *
from main.src.Entity.SW5.SW5CustomerEntity import SW5CustomerEntity
from main.src.Repository.functions_repository import parse_a_date
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import *


def sw5_delete_customer(adrnr):
    customer = SW5CustomerEntity(adrnr=adrnr, sw5_api=client_from_env(), mandant='58')
    customer.delete_erp_dataset_webshopid()
    # customer_address.delete_sw5_customer()



def sw5_sync_duplicates_v2(false_adrnr, right_adrnr):
    ###
    # 1. Create connection to ERP
    erp_connect('58')

    sw5_api = client_from_env()
    ###
    # 2. Make dict for false and right and create the object (get the dataset)
    # Get webshopid, amazonid an email from erp
    right_customer = SW5CustomerEntity(adrnr=right_adrnr, mandant='58', sw5_api=sw5_api)
    false_customer = SW5CustomerEntity(adrnr=false_adrnr, mandant='58', sw5_api=sw5_api)

    logger.info("###\nStart Right Customer: \n###\n", right_customer)
    logger.info("###\nStart False Customer: \n###\n", false_customer)
    ###
    # 3.1 Sync Webshop ID
    # Whether we keep the webshopid or we have to use the false
    right_customer.sync_webshop_id(false_customer=false_customer)

    # 3.2 Sync Amazon ID
    # Whether we keep the amazonid or we have to use the false
    right_customer.sync_amazon_id(false_customer=false_customer)

    # 3.3 Sync login fields
    # Whether we keep to fields or we have to use the false
    right_customer.sync_last_login_fields_sw5(false_customer=false_customer)

    right_customer.sync_orders(false_customer=false_customer)
    right_customer.sync_addresses(false_customer=false_customer)

    logger.info("###\nAddresses and Orders Right Customer: \n###\n", right_customer)
    logger.info("###\nAddresses and Orders False Customer: \n###\n", false_customer)
    return
    ###
    # Deleting/Updating
    ###

    ###
    # 1 ERP Delete false customer_address
    false_customer.delete_erp_dataset_adresse()
    # 2 Update right customer_address
    right_customer.set_erp_email()
    right_customer.set_erp_ids()

    # 3 SW5 Delete false customer_address
    # Delete false Customer from API
    # If we take the webshopid from false. Do not delete!
    if false_customer.get_webshopid() is not right_customer.get_webshopid():
        false_customer.delete_sw5_customer()

    right_customer.sync_customer_addresses_orders_and_credentials()

    # Close ERP Connection!!!!
    erp_close()


def sync_webshop_id(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity):
    """
    If right_customer has a webshop ID, keep it. If the right customer_address has none but false_customer has one. take it.
    If both have no webshop ID set it to False.
    :param right_customer: SW5CustomerEntity
    :param false_customer: SW5CustomerEntity
    :return: Boolean
    """
    # Case 1: right_customer has Webshop ID:
    if right_customer.get_webshopid():
        print("%s - Right customer_address has a Webshop ID. We keep it: %s \n" % (
            right_customer.get_adrnr(),
            right_customer.get_webshopid())
              )
        return True

    # Case 2 : right_customer has no Webshop ID. Has false_customer one?
    elif false_customer.get_webshopid():
        print("%s - False customer_address has a Webshop ID. We take it from there: %s\n" % (
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
        If right customer_address has an amazon ID, keep it. If the right customer_address has none but false customer_address has one. Take it.
        If both have no amazon ID set it to False.
        :param right_customer: SW5CustomerEntity
        :param false_customer: SW5CustomerEntity
        :return: Boolean
        """
    # Case 1: right_customer has Amazon ID:
    if right_customer.get_amazonid():
        print("%s - Right customer_address has a Amazon ID. We keep it: %s\n" % (
            right_customer.get_adrnr(),
            right_customer.get_amazonid())
              )
        return True

    # Case 2 : right_customer has no Amazon ID. Has false_customer one?
    elif false_customer.get_amazonid():
        print("%s - False customer_address has a Amazonp ID. We take it from there: %s\n" % (
            false_customer.get_adrnr(),
            false_customer.get_amazonid())
              )
        right_customer.set_amazonid(false_customer.get_amazonid())
        return True

    else:
        print("No Amazon ID found \n")
        right_customer.set_amazonid(False)
        return False


def sync_last_login_fields_sw5(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity, api: APIClient):
    """
    Get the most recent login date and set the password and password encoder to the right customer_address
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
            "False was most recently logged in: %s < %s. We need to take the password and the encoder from false customer_address" % (
                right_customer.get_last_login(), false_customer.get_last_login()))
        # Set Customer fields in the SW5CustomerEntity
        right_customer.set_last_login(false_customer.get_last_login())
        right_customer.set_password_hash(false_customer.get_password_hash())
        right_customer.set_password_encoder(false_customer.get_password_encoder())
        right_customer.set_email(false_customer.get_email())
    return True


def sync_orders_sw5(right_customer: SW5CustomerEntity, false_customer: SW5CustomerEntity, api: APIClient):
    """
    Get the orders for each customer_address and assign all the false customer_address orders to the right customer_address
    :param right_customer: object SW5CustomerEntity
    :param false_customer: object SW5CustomerEntity
    :param api: object APIClient
    :return: bool
    """
    # Get th orders
    right_customer.set_orders(api.get_order_by_customerId(right_customer.get_webshopid()))
    false_customer.set_orders(api.get_order_by_customerId(false_customer.get_webshopid()))

    # Now set every order of false customer_address to right customer_address
    for order in false_customer.get_orders():
        # print("Order Id: %s - CustomerId: %s -> CustomerId: %s" % (
        #     order['id'], order['customerId'], right_customer.get_webshopid()))
        api.set_order_customerId_by_orderId(right_customer.get_webshopid(), order['id'])

    # After setting all the orders in SW5, get them from the api and set them to the customer_address object
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
