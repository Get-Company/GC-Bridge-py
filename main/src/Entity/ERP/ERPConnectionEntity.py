"""
This Object is for creating the connection to büro+ microtech. You can get all different Datasets
"""
import win32com.client as win32
import pythoncom
import pywintypes
import logging


from loguru import logger
import win32com.client as win32
import pythoncom
import pywintypes

class ERPConnectionEntity:
    _instance = None  # Singleton instance
    _connection = None  # Connection instance

    def __init__(self, mandant="58"):
        """
        Initialize the ERPConnectionEntity.
        :param mandant: The default mandant. Defaults to "58".
        """
        # Initialisierung
        self.erp = None
        self.mandant = None
        self.mand_state = None
        self.max_reconnections = 3
        self.count_reconnects = 0
        self.dataset = None

        logger.info("ERPConnectionEntity initialized with mandant %s", mandant)

        # Mandant setzen und ERP initialisieren
        self.set_erp()
        self.set_mandant(mandant)

    def __del__(self):
        self.close()

    def set_erp(self):
        """Sets the BpNT.Application COM object."""
        pythoncom.CoInitialize()
        try:
            self.erp = win32.dynamic.Dispatch("BpNT.Application")
            logger.info("BpNT.Application dispatched successfully")
        except pywintypes.com_error as e:
            logger.error("COM dispatch error: {}", e)
            self.erp = None

    def get_erp(self):
        """Return the COM object or raise if not available."""
        if not self.erp:
            logger.error("ERP COM object is not initialized.")
            raise RuntimeError("ERP COM object is not initialized.")
        return self.erp

    def set_mandant(self, mandant):
        """Set the mandant identifier."""
        self.mandant = str(mandant)
        logger.info("Mandant set to %s", self.mandant)

    def get_mandant(self):
        """Return the mandant identifier or raise if missing."""
        if not self.mandant:
            logger.warning("Mandant not set.")
            raise RuntimeError("Mandant not set.")
        return self.mandant

    def connect(self, firma="Egon Heimann GmbH", benutzer="GC-Autosync"):
        """
        Establish a connection with the given credentials.
        :param firma: Company name
        :param benutzer: Username
        :return: True if successful, False otherwise
        """
        # Überprüfe ERP-Objekt
        try:
            self.get_erp()
        except Exception as e:
            logger.warning("Cannot connect: {}", e)
            return False

        # Verbindung aufbauen
        try:
            self.erp.Init(firma, "", benutzer, "")
            self.erp.SelectMand(self.get_mandant())
            logger.info("ERP connected: mandant=%s, user=%s", self.get_mandant(), benutzer)
        except pywintypes.com_error as e:
            logger.error("ERP COM error on Init/SelectMand: {}", e)
            return False
        except Exception as e:
            logger.error("Unexpected error during ERP connect: {}", e)
            return False

        return True

    def close(self):
        """
        Close the ERP connection and release resources.
        :return: True if closed cleanly, False otherwise
        """
        if not self.erp:
            logger.info("No ERP connection to close.")
            return False

        try:
            # LogOff oder DeInit je nach API
            if hasattr(self.erp, 'LogOff'):
                self.erp.LogOff()
            elif hasattr(self.erp, 'DeInit'):
                self.erp.DeInit()
            logger.info("ERP connection closed successfully.")
        except Exception as e:
            logger.warning("Error during ERP disconnection: {}", e)
            return False
        finally:
            self.erp = None

        return True
