import datetime
import pytz
# To get the method names
import inspect

import logging

# Own
from main.src.Controller.ERP.ERPController import *

# functions
import dateparser


class SW5CustomerEntity:
    def __init__(self, adrnr, sw5_api, mandant="Test"):
        # Define Attributes
        self.adrnr = None
        self.webshopid = None
        self.amazonid = None
        self.email = None

        self.last_login = None
        self.password_hash = None
        self.password_encoder = None

        self.orders = []
        self.addresses = []

        self.mandant = mandant
        self.dataset_adresse = None
        self.dataset_anschrift = None

        self.sw5_api = sw5_api

        self.class_name = self.__class__.__name__


        ###
        # Functions that collect infos from erp and webshop
        ###
        self.set_adrnr(adrnr)

        # Get ERP Infos
        self.set_erp_customer_infos()

        # Get webshop customer_address infos
        if self.get_webshopid():
            # lastlogin, password, encoder
            self.set_sw5_customer_infos()
            # Get all orders
            self.set_orders()
            # Get all addresses
            self.set_addresses()

        self.set_dataset_adresse()
        self.set_dataset_anschrift()

    def __repr__(self):
        return ("This is customer_address "
                "AdrNr: %s, \n"
                "WebshopId: %s, \n"
                "AmazonId: %s, \n"
                "E-Mail:%s, \n"
                "Last Login SW5: %s, \n"
                "Password Hash: %s, \n"
                "Password Encoder: %s, \n"
                "Orders IDs: %s, \n"
                "Adresses Ids: %s \n"
                % (
                    self.get_adrnr(),
                    self.get_webshopid(),
                    self.get_amazonid(),
                    self.get_email(),
                    self.get_last_login(),
                    self.get_password_hash(),
                    self.get_password_encoder(),
                    self.get_orders_ids(),
                    self.get_addresses_ids()
                ))

    def print_method_info(self, message=False):
        print('\n#- %s %s -#' % (self.class_name, inspect.currentframe().f_back.f_code.co_name))
        if message:
            print(message)

    def set_sw5_customer_infos(self):
        """
        Forward the return from the api to this function (['data'])
        :param sw5_api_customer_data:
        :return:
        """

        # self.print_method_info()
        if not self.get_webshopid():
            return False
        else:
            sw5_data = self.sw5_api.get_customer(self.get_webshopid())

        # Set Last Login
        self.set_last_login(sw5_data['lastLogin'])

        # Set Password
        self.set_password_hash(sw5_data['hashPassword'])

        # Set Encoder
        self.set_password_encoder(sw5_data['encoderName'])

        return True

    def set_erp_customer_infos(self, connect=False):
        """
        Connects to ERP with mandant. Sets self.amazonid and self.webshopid
        :return: Bool
        """
        if connect:
            erp_connect(self.mandant)

        adressen = erp_get_dataset('Adressen')
        erp_get_dataset_by_id(adressen, 'Nr', self.adrnr)

        # Get WebshopID
        if adressen.Fields.Item("WShopID").AsString:
            self.set_webshopid(adressen.Fields.Item("WShopID").AsInteger)
        else:
            self.set_webshopid(False)

        # Get AmazonID
        if adressen.Fields.Item("AucWebID").AsString:
            self.set_amazonid(adressen.Fields.Item("AucWebID").AsString)
        else:
            self.set_amazonid(False)

        # Get E-Mail
        anschrift = erp_get_dataset('Anschriften')
        erp_get_dataset_by_id(anschrift, 'AdrNrAnsNr', self.adrnr)

        if anschrift.Fields.Item('EMail1').AsString:
            self.set_email(anschrift.Fields.Item('EMail1').AsString)
        else:
            self.set_email(False)

        if connect:
            erp_close()

        return True

    def reset_ids_erp_customer(self):

        self.set_ids_erp(False, False)

        return True

    def sync_webshop_id(self, false_customer):
        """
        If rself has a webshop ID, keep it. If the right customer_address has none but false_customer has one. take it.
        If both have no webshop ID set it to False.
        :param right_customer: SW5CustomerEntity
        :param false_customer: SW5CustomerEntity
        :return: Boolean
        """
        # Case 1: right_customer has Webshop ID:
        if self.get_webshopid():
            print("%s - Right customer_address has a Webshop ID. We keep it: %s \n" % (
                self.get_adrnr(),
                self.get_webshopid())
                  )
            return True

        # Case 2 : right_customer has no Webshop ID. Has false_customer one?
        # Take the creden tials
        elif false_customer.get_webshopid():
            print("%s - False customer_address has a Webshop ID. We take it from there: %s\n" % (
                false_customer.get_adrnr(),
                false_customer.get_webshopid())
                  )
            self.set_webshopid(false_customer.get_webshopid())
            self.set_email(false_customer.get_email())
            return True

        else:
            print("No Webshop ID found \n")
            self.set_webshopid(False)
            return False

    def sync_amazon_id(self, false_customer):
        """
            If right customer_address has an amazon ID, keep it. If the right customer_address has none but false customer_address has one. Take it.
            If both have no amazon ID set it to False.
            :param right_customer: SW5CustomerEntity
            :param false_customer: SW5CustomerEntity
            :return: Boolean
            """
        # Case 1: right_customer has Amazon ID:
        if self.get_amazonid():
            print("%s - Right customer_address has a Amazon ID. We keep it: %s\n" % (
                self.get_adrnr(),
                self.get_amazonid())
                  )
            return True

        # Case 2 : right_customer has no Amazon ID. Has false_customer one?
        elif false_customer.get_amazonid():
            print("%s - False customer_address has a Amazonp ID. We take it from there: %s\n" % (
                false_customer.get_adrnr(),
                false_customer.get_amazonid())
                  )
            self.set_amazonid(false_customer.get_amazonid())
            return True

        else:
            print("No Amazon ID found \n")
            self.set_amazonid(False)
            return False

    def sync_last_login_fields_sw5(self, false_customer):
        """
        Get the most recent login date and set the password and password encoder to the right customer_address
        :param right_customer: object SW5CustomerEntity
        :param false_customer:  object SW5CustomerEntity
        :param api: object APIClient
        :return: Bool
        """
        older_date = datetime.datetime(1900, 1, 1, 10, 10, 10, 10, pytz.UTC)
        if self.get_last_login():
            print("Right has lastlogn")
        else:
            print("Right hast no lastlogin, we set 01.01.1900")
            self.set_last_login(older_date)

        if false_customer.get_last_login():
            print("False has lastlogin")
        else:
            print("False has no lastlogin, we set 01.01.1900")
            false_customer.set_last_login(older_date)

        if self.get_last_login() > false_customer.get_last_login():
            print("Right was most recently logged in: %s > %s. We keep all fields!" % (
                self.get_last_login(), false_customer.get_last_login()))
            return True
        else:
            print(
                "False was most recently logged in: %s < %s. We need to take the password and the encoder from false customer_address" % (
                    self.get_last_login(), false_customer.get_last_login()))
            # Set Customer fields in the SW5CustomerEntity
            self.set_last_login(false_customer.get_last_login())
            self.set_password_hash(false_customer.get_password_hash())
            self.set_password_encoder(false_customer.get_password_encoder())
            self.set_email(false_customer.get_email())
        return True

    def sync_orders(self, false_customer):
        if false_customer.get_orders:
            self.add_orders(false_customer.get_orders)
            return True
        else:
            return False

    def sync_addresses(self, false_customer):
        if false_customer.get_addresses():
            self.add_addresses(false_customer.get_addresses())
            return True
        else:
            return False

    def sync_customer_addresses_orders_and_credentials(self):
        # 1. Customer
        # Todo: The  email could be already in the db. Following code wont run, bc SW detects duplicate emails. So we need to changes the wrong duplicate emails in a for loop
        # Get all customers by email but not with the right_id. Replace email with new one, use credentials from  return
        duplicate_customers = self.sw5_api.get_customer_filter_by_email_and_not_like_id(self.get_webshopid(), self.get_email())
        for index, duplicate_customer in enumerate(duplicate_customers):
            new_email = str(index)+duplicate_customer['email']
            self.sw5_api.set_customer_credentials_by_customerId(
                customerId=duplicate_customer['id'],
                password=duplicate_customer['hashPassword'],
                encoder_name=duplicate_customer['encoderName'],
                last_login=duplicate_customer['lastLogin'],
                email=new_email
            )
            new_email = None

        # 2 Addresses
        if self.get_addresses_ids():
            for address_id in self.get_addresses_ids():
                self.sw5_api.set_address_by_id(address_id, self.get_webshopid())
        # 3. Orders
        if self.get_orders_ids():
            for order_id in self.get_orders_ids():
                self.sw5_api.set_order_customerId_by_orderId(self.get_webshopid(), order_id)

        # 4. Credentials
        updated_customer = self.sw5_api.set_customer_credentials_by_customerId(
            customerId=self.get_webshopid(),
            password=self.get_password_hash(),
            encoder_name=self.get_password_encoder(),
            last_login=self.get_last_login(),
            email=self.get_email()
        )

        self.sw5_api.set_customer_adrnr_by_Id(self.get_webshopid(), self.get_adrnr())
        return updated_customer

    def delete_sw5_customer(self):
        self.sw5_api.delete_customer_by_customerId(self.get_webshopid())

    """
    Getter and setter Methods
    """

    # Adressnummer
    def set_adrnr(self, adrnr):
        if adrnr and adrnr is not str:
            adrnr = str(adrnr)
        self.adrnr = adrnr

    def get_adrnr(self):
        return self.adrnr

    # Webshop ID
    def set_webshopid(self, webshopid):
        # First check if False is given.
        if not webshopid:
            self.webshopid = False
        # If not, convert the var inti int
        elif type(webshopid) is not int:
            self.webshopid = int(webshopid)
        # If it is already an int: Simply assign it
        else:
            self.webshopid = webshopid

    def get_webshopid(self):
        if self.webshopid:
            return self.webshopid
        else:
            return False

    # Amazon ID
    def set_amazonid(self, amazonid):
        # First check if False is given.
        if not amazonid:
            self.amazonid = False
        # If not, convert the var inti int
        elif type(amazonid) is not str:
            self.amazonid = str(amazonid)
        # If it is already an int: Simply assign it
        else:
            self.amazonid = amazonid

    def get_amazonid(self):
        return self.amazonid

    # E-Mail
    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email

    # Lastlogin
    def set_last_login(self, last_login):
        # self.print_method_info('Last Login: %s by AdrNr: %s' % (last_login, self.get_adrnr()))
        # Sometimes we get none or empty. Since we must have a date -> Make it far away in the past
        if last_login is None:
            print("No Date, whether str nor any other was given. NoneType. Let's make 01.01.1800")
            last_login = datetime.date(1900, 1, 1)

        if type(last_login) is str:
            print("Last Login was given as string. Parsing it to Date")
            last_login = dateparser.parse(last_login)

        self.last_login = last_login
        return True

    def get_last_login(self):
        """
        Last Login is returned as datetime object
        :return: datetime object
        """
        return self.last_login

    # Password Hash
    def set_password_hash(self, password_hash):
        self.password_hash = password_hash

    def get_password_hash(self):
        return self.password_hash

    # Password Encoder
    def set_password_encoder(self, password_encoder):
        self.password_encoder = password_encoder

    def get_password_encoder(self):
        return self.password_encoder

    # Orders
    def set_orders(self):
        orders = self.sw5_api.get_orders_by_customerId(self.get_webshopid())
        for order in orders:
            self.orders.append(order)

        return True

    def add_orders(self, orders):
        if len(self.orders):
            for order in orders:
                self.orders.append(order)

        return True

    def get_orders(self):
        if self.orders:
            return self.orders
        else:
            return False

    def get_orders_ids(self):
        if len(self.orders):
            orders_ids = []
            for order in self.get_orders():
                orders_ids.append(order['id'])
            return orders_ids
        else:
            return False

    def unset_orders(self):
        """
        Simply clears/empties the list. Is used by SW5AdressController in sync_orders_sw5. Befor getting all new
        assigned orders, the list must be empty.
        :return:
        """
        self.orders.clear()

    # Addresses
    def set_addresses(self):
        addresses = self.sw5_api.get_addresses_by_id(self.get_webshopid())
        self.addresses.append(addresses)

    def add_addresses(self, addresses):
        for address in addresses:
            self.addresses.append(address)

        return True

    def get_addresses(self):
        if self.addresses:
            return self.addresses
        else:
            return False

    def get_addresses_ids(self):
        if len(self.addresses):
            addresses_ids = []
            for address in self.addresses:
                print(address['id'])
                addresses_ids.append(address['id'])
            return addresses_ids
        else:
            return False

    # Mandant
    def set_mandant(self, mandant):
        self.mandant = mandant

        return True

    def get_mandant(self):
        return self.mandant

    # Dataset ERP
    def set_dataset_adresse(self, connect=False):
        if connect:
            erp_connect(self.mandant)

        # self.print_method_info()

        adressen = erp_get_dataset('Adressen')
        erp_get_dataset_by_id(adressen, 'Nr', self.get_adrnr())
        self.dataset_adresse = adressen

        if connect:
            erp_close()

        return True

    def get_dataset_adresse(self):
        return self.dataset_adresse

    def set_dataset_anschrift(self, connect=False):
        if connect:
            erp_connect(self.mandant)

            anschrift = erp_get_dataset('Anschriften')
            erp_get_dataset_by_id(anschrift, 'AdrNrAnsNr', self.get_adrnr())
            self.dataset_anschrift = anschrift

            if connect:
                erp_close()

    def get_dataset_anschrift(self):
        return self.dataset_anschrift

    def delete_erp_dataset_adresse(self, connect=False):
        if connect:
            erp_connect(self.mandant)

        adresse = self.get_dataset_adresse()
        adresse.Edit()
        adresse.Delete()

        try:
            adresse.Post()
            adresse.Commit()

            if connect:
                erp_close()

            return True
        except:
            adresse.Cancel()

            if connect:
                erp_close()

            return False

    def delete_erp_dataset_webshopid(self, connect=False, adrnr=None):
        if connect:
            erp_connect(self.mandant)

        adressen = erp_get_dataset('Adressen')
        erp_get_dataset_by_id(adressen, 'Nr', self.get_adrnr())

        adressen.Edit()

        # WebshopID
        if self.get_webshopid():

            if type(self.get_webshopid()) is not str:
                webshopid = str(self.get_webshopid())
            else:
                webshopid = self.get_webshopid()

            adressen.Fields("WShopAdrKz").AsBoolean = False
            adressen.Fields("WShopID").AsString = ''

        try:
            adressen.Post()
            adressen.Commit()

            if connect:
                erp_close()

            return True
        except:
            adressen.Cancel()
            if connect:
                erp_close()
            return False

    # Set the Webshop ID in ERP for Adresse by Adrnr.
    def set_erp_ids(self, connect=False):
        """
        Take all the ids for the address an change them. Sepparate functions (webshopID and AmazonID) didn't work. Maybe
        because of the .Pos(). Be sure to set all the ids, they are overwritten in this function
        We nedd to make the change for all fields and Post afterwarts.
        :param connect: Boolean. Set True for creating a connection. This is usefull if we need this function as standalone
        :param webshopid: Any form it is converted to string
        :param amazonid: any form, it is converted to string
        :return:
        """
        if connect:
            erp_connect(self.mandant)

        adressen = erp_get_dataset('Adressen')
        erp_get_dataset_by_id(adressen, 'Nr', self.get_adrnr())

        adressen.Edit()

        # WebshopID
        if self.get_webshopid():

            if type(self.get_webshopid()) is not str:
                webshopid = str(self.get_webshopid())
            else:
                webshopid = self.get_webshopid()

            adressen.Fields("WShopAdrKz").AsBoolean = True
            adressen.Fields("WShopID").AsString = webshopid

        else:
            adressen.Fields("WShopAdrKz").AsBoolean = False
            adressen.Fields("WShopID").AsString = ''

        # AmazonID
        if self.get_amazonid():

            if type(self.get_amazonid()) is not str:
                amazonid = str(self.get_amazonid())
            else:
                amazonid = self.get_amazonid()

            adressen.Fields("AucWebKz").AsBoolean = True
            adressen.Fields("AucWebID").AsString = amazonid

        else:
            adressen.Fields("AucWebKz").AsBoolean = False
            adressen.Fields("AucWebID").AsString = ''


        try:
            adressen.Post()
            adressen.Commit()

            if connect:
                erp_close()

            return True
        except:
            adressen.Cancel()
            if connect:
                erp_close()
            return False

    # Set the email in Anschrift
    def set_erp_email(self, connect=False):
        if connect:
            erp_connect()

        anschrift = erp_get_dataset('Anschriften')
        erp_get_dataset_by_id(anschrift, 'AdrNrAnsNr', self.get_adrnr())

        anschrift.Edit()

        if self.get_webshopid() and self.get_email():
            anschrift.Fields.Item('EMail1').AsString = self.get_email()

        try:
            anschrift.Post()
            anschrift.Commit()

            if connect:
                erp_close()

            return True
        except:
            anschrift.Cancel()
            if connect:
                erp_close()
            return False




