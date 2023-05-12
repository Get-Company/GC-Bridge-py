"""
Example:
    # Verbindung zu Büro+
    erp_obj = ERPConnectionEntity(mandant=58)
    erp_obj.connect()
    # Create Object
    bestellung = ERPVorgangEntity(erp_obj=erp_obj)
    # Create the new dataset
    bestellung.create_new_webshop_order('10026')
    # Ask for Artikel 1
    artikel1 = ERPArtikelEntity(erp_obj=erp_obj, id_value='204116')
    # Add Artikel 1
    bestellung.add_position(100, artikel1.get_('Einh'), '204116')
    # Ask for Artikel2
    artikel2 = ERPArtikelEntity(erp_obj=erp_obj, id_value='581000')
    # Add Artikel2
    bestellung.add_position(20, artikel2.get_('Einh'), '581000')
    # Post everything
    bestellung.post_dataset()
"""
import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity
import datetime


class ERPVorgangEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):
        self.erp_obj = erp_obj
        self.dataset_name = 'Vorgang'
        self.dataset_id_field = 'AdrNr'
        self.dataset_id_value = id_value
        self.dataset_range = dataset_range

        self.prefill_json_directory = "main/src/json/order/"

        self.created_dataset = self.erp_obj.get_erp().GetSpecialObject(1)

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            prefill_json_directory=self.prefill_json_directory
        )

    """ CRUD """

    def create_new_order(self):
        self.order = self.erp_obj.get_erp().GetSpecialObject(1)

    def create_new_webshop_order(self, order, positions):
        self.create_new_order()
        self.order.Append(111, order.customer.erp_nr)
        self.created_dataset = self.order.Dataset
        self.create_("AuftrNr", "SW6_"+order.api_id)
        self.prefill_from_file(
            file=self.prefill_json_directory + "shopware6/rechnung/germany.yaml"
        )
        for pos in positions['order_products']:
            print(pos["name"])
            self.add_position(
                quantity=pos["quantity"],
                artnr=pos["erp_nr"]
            )
        self.post_dataset()

    def create_new_webshop_order_v2(self, adrnr):
        self.Append(111, adrnr)
        self.prefill_from_file(
            file=self.prefill_json_directory + "shopware6/rechnung/germany.yaml"
        )
        self.create_("AuftrNr", "SW6_"+self.order.api_id)
        self.dataset.Positionen.Add(10, "St", 104014)
        return self.get_("BelegNr")

    def add_position(self, quantity, artnr):
        """
        Adds a new row to self.order
        :param quantity: int Menge ex: 100
        :param unit: str Verpackungseinheit ex: "Stck" oder "% Stck"
        :param artnr: str Artikelnummer ex: "204116"
        :return:
        """
        print("Add Position: ", quantity, artnr)
        artikel = ERPArtikelEntity(erp_obj=self.erp_obj, id_value=artnr)
        self.order.Positionen.Add(quantity, artikel.get_('Einh'), artnr)
        artikel = None

    def post_dataset(self):
        try:
            self.order.Post()
        except:
            self.created_dataset.Cancel()
            logging.warning("Post/Commit could not execute. Rollback was called. Regarding Dataset: %s" %
                            self.get_dataset_name())


