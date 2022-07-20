import win32com.client as win32
import pythoncom
import logging


class ERPObjectController:
    def __init__(self, mandant="Test"):
        self.mandant = None
        self.erp = None
        self.mand_state = None
        self.max_reconnections = 3
        self.count_reconnects = 0

        self.dataset = None

        # loggin setup
        logging.basicConfig(
            filename="logfiles/ERPObjectController.log"
        )
        logging.info("Log Initialized")

        # functions
        # self.set_erp()
        self.connect()

    def __del__(self):
        logging.info("The destructor __del__ was called, which calls the function close()")
        self.close()

    """
    Getter & Setter
    """

    # ERP
    def set_erp(self):
        """
        Sets the BpNT.Application
        """
        if self.erp:
            logging.warning("ERP existed. Closed.")
            self.close()
        else:
            pythoncom.CoInitialize()
            self.erp = win32.dynamic.Dispatch("BpNT.Application")
            logging.info("BpNT is dispatched")

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
        self.mandant = mandant

    def get_mandant(self):
        if self.mandant:
            return self.mandant
        else:
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
            logging.info(
                "Getting Mandant State: %s \n 0=ok, 1=Tageswechsel durchgeführt, 2=Parameteränderung durchgeführt" % self.mand_state)
            return self.mand_state

    # Dataset
    def set_dataset(self, dataset):
        if self.dataset:
            self.dataset = None

        logging.info("Get dataset: %s" % dataset)
        dataset_infos = self.erp.DataSetInfos.Item(dataset)
        self.dataset = dataset_infos.CreateDataSet()
        logging.info("Dataset loaded: %s" % self.dataset)

    def get_dataset(self):
        return self.dataset

    def get_dataset_by_id(self, dataset, field, value):
        self.set_dataset(dataset=dataset)

        found = self.get_dataset().FindKey(field, value)
        if found:
            return found

    """
    Functions
    """

    def connect(self):
        """
        The connection with the given credentials will be established. The fields are:
        Firmenname, Solution Partner ID (bleibt Leer), Anmeldename, Passwort
        :return:
        """
        # 1 Check if erp is available. Avoid duplicate connections
        try:
            self.get_erp()
        except UnboundLocalError:
            logging.warning("No ERP to connect. Did you created it? self.set_erp")
        else:
            print("No Problems with the connection")
        finally:
            print("This is ERP: %s" % self.get_erp)

    def close(self):
        """
        The connection will be closed by LogOff() and the object ist set to None. For another connection,
        selfset_erp needs to be called again.
        :return:
        """
        self.erp.DeInit()
        logging.info("ERP is closed")
        return True
