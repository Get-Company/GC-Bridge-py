"""
This Object is for creating the connection to büro+ microtech. You can get all different Datasets
"""
import win32com.client as win32
import pythoncom
import pywintypes
import logging


class ERPConnectionEntity:
    def __init__(self, mandant="58"):

        self.mandant = None
        self.erp = None
        self.mand_state = None
        self.max_reconnections = 3
        self.count_reconnects = 0

        self.auto_vorgang = None

        self.dataset = None

        self.logging = logging

        # loggin setup
        self.logging.basicConfig(
            filename="logfiles/ERPObjectEntity.log"
        )
        self.logging.info("Log Initialized")

        # functions
        self.set_erp()
        self.set_mandant(mandant=mandant)
        # self.connect()

    def __del__(self):
        self.close()

    """
    Getter & Setter
    """

    # ERP
    def set_erp(self):
        """
        Sets the BpNT.Application
        """
        pythoncom.CoInitialize()
        self.erp = win32.dynamic.Dispatch("BpNT.Application")
        self.logging.info("BpNT is dispatched")

    def get_erp(self):
        """
        Check if erp ist set and return it. The pythoncom.CoInitialize is necessary for the flask server.
        It initializes the com instance for the calling thread. So its callablöe multiple times (hopefully)
        :return: com object erp BpNT.Application
        """
        if self.erp:
            return self.erp


    # Mandant
    def set_mandant(self, mandant):
        self.mandant = str(mandant)

    def get_mandant(self):
        if self.mandant:
            return self.mandant
        else:
            self.logging.warning("No mandant available")
            return False

    def set_mandant_state(self):
        """
        Check for the state of the mandand. only connect when 0 is returned
        0=ok,
        1=Tageswechsel durchgeführt,
        2=Parameteränderung durchgeführt
        :return:
        """
        self.mand_state = self.get_erp().GetMandState()

    def get_mandant_state(self):
        if self.mand_state:
            self.logging.info(
                "Getting Mandant State: %s \n 0=ok, 1=Tageswechsel durchgeführt, 2=Parameteränderung durchgeführt" % self.mand_state)
            return self.mand_state



    """
    Functions
    """
    def connect(self, firma="Egon Heimann GmbH", benutzer="GC-Autosync"):
        """
        The connection with the given credentials will be established. The fields are:
        Firmenname, Solution Partner ID (bleibt Leer), Anmeldename, Passwort

        :return:
        """
        # 1 Check if erp is available. Avoid duplicate connections
        try:
            self.get_erp()
        except UnboundLocalError as e:
            self.logging.warning("No ERP to connect. Did you created it? self.set_erp")
        except pywintypes.com_error as e:
            print(e)
        else:
            self.erp.Init(f'{firma}', "", f'{benutzer}', '')
            self.erp.SelectMand(self.get_mandant())
            print("ERP connects to:", self.get_mandant(), "with user:", benutzer)
        finally:
            print("Connected: This is ERP: %s" % self.get_erp())

    def close(self):
        """
        The connection will be closed by LogOff() and the object ist set to None. For another connection,
        selfset_erp needs to be called again.
        :return:
        """
        try:
            self.erp.DeInit()
            self.erp = None
        except:
            self.logging.warning("Cannot DeInit. Object is NoneType")
        else:
            self.logging.info("ERP is closed")
            print("Closed: This is ERP: %s" % self.get_erp())
            return True

    def set_cursor_to_field_value(self, field, value):
        self.dataset.FindKey(field, value)
