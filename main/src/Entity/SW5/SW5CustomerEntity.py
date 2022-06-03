import datetime
# To get the method names
import inspect

from main.src.Controller.ERP.ERPController import *

# functions
import dateparser


class SW5CustomerEntity:
    def __init__(self, adrnr, mandant="Test"):
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

        self.class_name = self.__class__.__name__

        # Functions
        self.set_adrnr(adrnr)
        self.get_erp_customer_infos()
        self.set_dataset_adresse()

    def __repr__(self):
        return ("This is customer "
                "AdrNr: %s, "
                "WebshopId: %s, "
                "AmazonId: %s, "
                "E-Mail:%s, "
                "Last Login SW5: %s, "
                "Password Hash: %s,"
                "Password Encoder: %s,"
                "Orders IDs: %s,"
                "Adresses Ids: %s"
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

    def set_fields_from_sw5(self, sw5_data):
        """
        Forward the return from the api to this function (['data'])
        :param sw5_api_customer_data:
        :return:
        """
        self.print_method_info()

        # Set Last Login
        self.set_last_login(sw5_data['lastLogin'])

        # Set Password
        self.set_password_hash(sw5_data['hashPassword'])

        # Set Encoder
        self.set_password_encoder(sw5_data['encoderName'])

        return True

    def get_erp_customer_infos(self, connect=False):
        """
        Connects to ERP with mandant. Sets self.amazonid and self.webshopid
        :return: Bool
        """
        if connect:
            erp_connect(self.mandant)

        self.print_method_info()

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

        print("WebshopID: %s, AmazonID: %s, E-Mail: %s \n" % (
        self.get_webshopid(), self.get_amazonid(), self.get_email()))

        if connect:
            erp_close()

        return True

    def reset_ids_erp_customer(self):

        self.set_ids_erp(False, False)

        return True

    """
    Getter and setter Methods
    """

    # Adressnummer
    def set_adrnr(self, adrnr):
        if adrnr and adrnr is not str:
            adrnr = str(adrnr)
        self.print_method_info('Setting AdrNr: %s \n' % adrnr)
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
        return self.webshopid

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
        self.print_method_info('Last Login: %s by AdrNr: %s' % (last_login, self.get_adrnr()))
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
    def set_orders(self, data):
        self.orders = data

    def get_orders(self):
        return self.orders

    def get_orders_ids(self):
        orders_ids = []
        for order in self.get_orders():
            orders_ids.append(order['id'])
        if orders_ids:
            return orders_ids
        else:
            return False

    def unset_orders(self):
        """
        Simply clears/emties the list. Is used by SW5AdressController in sync_orders_sw5. Befor gettin all new
        assigned orders, the list must be empty.
        :return:
        """
        self.orders.clear()

    # Addresses
    def set_addresses(self, addresses):
        self.addresses = addresses

    def get_addresses(self):
        return self.addresses

    def get_addresses_ids(self):
        addresses_ids = []
        for address in self.get_addresses():
            addresses_ids.append(address['id'])
        if addresses_ids:
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

        self.print_method_info()

        adressen = erp_get_dataset('Adressen')
        erp_get_dataset_by_id(adressen, 'Nr', self.get_adrnr())
        self.dataset_adresse = adressen

        if connect:
            erp_close()

        return True

    def get_dataset_adresse(self):
        return self.dataset_adresse

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

        adressen = self.get_dataset_adresse()
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
