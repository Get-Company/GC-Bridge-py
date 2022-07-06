from main.src.Entity.SW5.SW5CustomerEntity import SW5CustomerEntity
from .APIClient import *
from main.src.Controller.ERP.ERPController import *


class SW5AddressController:
    def __init__(self, false_adrnr, right_adrnr):
        erp_connect('58')
        self.right_adrnr = None
        self.false_adrnr = None
        self.right_customer = None
        self.false_customer = None
        self.sw5_api = None

        # functions
        self.set_sw5_api()
        self.set_false_adrnr(false_adrnr=false_adrnr)
        self.set_right_adrnr(right_adrnr=right_adrnr)
        self.set_false_customer(false_adrnr=self.get_false_adrnr())
        self.set_right_customer(right_adrnr=self.get_right_adrnr())
        erp_close()

    """
    Getter and Setter
    """
    def set_sw5_api(self):
        self.sw5_api = client_from_env()

    def get_sw5_api(self):
        if self.sw5_api:
            return self.sw5_api
        else:
            return False

    def set_false_adrnr(self, false_adrnr):
        self.false_adrnr = false_adrnr

    def get_false_adrnr(self):
        if self.false_adrnr:
            return self.false_adrnr

    def set_right_adrnr(self, right_adrnr):
        self.right_adrnr = right_adrnr

    def get_right_adrnr(self):
        if self.right_adrnr:
            return self.right_adrnr

    def set_false_customer(self, false_adrnr):
        self.false_customer = SW5CustomerEntity(adrnr=false_adrnr, mandant='58', sw5_api=self.get_sw5_api())

    def get_false_customer(self):
        return self.false_customer

    def set_right_customer(self, right_adrnr):
        self.right_customer = SW5CustomerEntity(adrnr=right_adrnr, mandant='58', sw5_api=self.get_sw5_api())

    def get_right_customer(self):
        return self.right_customer

    def __repr__(self):
        return ("This is false: %s and this is right: %s" % (self.get_false_adrnr(), self.get_right_adrnr()))