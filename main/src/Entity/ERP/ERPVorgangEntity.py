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
        order_number = "SW6_" + order.api_id
        self.create_new_order()
        self.order.Append(111, order.customer.erp_nr)
        self.created_dataset = self.order.Dataset
        self.create_("AuftrNr", order_number)
        self.create_("Bez", f"GC Webshop-Bestellung Nr. EC{order.order_number} vom {order.purchase_date} {order.payment_method} - Versand {order.shipping_method}")

        payment_method = order.payment_method.replace(" ", "_").lower()
        shipping_method = order.shipping_method.lower()
        specific_path = f"shopware6/{payment_method}/{shipping_method}.yaml"
        general_path = "shopware6/rechnung/de.yaml"
        print("looking for", specific_path)
        try:
            self.prefill_from_file(
                file=self.prefill_json_directory + specific_path
            )
        except FileNotFoundError as e:
            print("Error:", e, "Could not open", specific_path, "Using:", general_path)
            self.prefill_from_file(
                file=self.prefill_json_directory + general_path
            )
        for pos in positions['order_products']:
            print(pos["name"])
            # This is a test to recognise the order as CH - no tax!
            if order.shipping_method == "CH":
                self.add_position(
                    quantity=pos["quantity"],
                    artnr=pos["erp_nr"],
                    price=pos["unit_price"],
                    steuer="10 Umsatzsteuerfrei (Verkauf)"
                )
                info_blatt = self.created_dataset.NestedDataSets('VIBls')

            else:
                self.add_position(
                    quantity=pos["quantity"],
                    artnr=pos["erp_nr"],
                    price=pos["unit_price"]
                )
        if order.shipping_costs:
            self.add_position_shipping(
                quantity=1,
                artnr="V",
                price=order.shipping_costs
            )

        self.post_dataset()

        return order_number

    def add_position(self, quantity, artnr, price=None, steuer=None):
        """
        Adds a new row to self.order
        :param quantity: int Menge ex: 100
        :param unit: str Verpackungseinheit ex: "Stck" oder "% Stck"
        :param artnr: str Artikelnummer ex: "204116"
        :Param price: float Preis: if none, the standard Price is used from büro+
        :return:
        """
        print("Add Position: ", quantity, artnr)
        artikel = ERPArtikelEntity(erp_obj=self.erp_obj, id_value=artnr)
        self.order.Positionen.Add(quantity, artikel.get_('Einh'), artnr)
        if price:
            self.order.Positionen.Dataset.Edit()
            betrag = self.order.positionen.DataSet.Fields("EPr").GetEditObject(2)
            betrag.clear()
            betrag.GesNetto = price

            betrag.Save()
            self.order.Positionen.DataSet.Post()
        artikel = None

    def add_position_shipping(self, quantity, artnr, price=None):
        artikel = ERPArtikelEntity(erp_obj=self.erp_obj, id_value=artnr)
        self.order.Positionen.Add(quantity, artikel.get_('Einh'), artnr)
        self.order.Positionen.Dataset.Edit()
        betrag = self.order.positionen.DataSet.Fields("EPr").GetEditObject(2)
        betrag.clear()
        betrag.GesNetto = price
        betrag.Save()
        self.order.Positionen.DataSet.Post()
        artikel = None
        betrag = None

    def post_dataset(self):
        try:
            self.order.Post()
        except:
            self.created_dataset.Cancel()
            logging.warning("Post/Commit could not execute. Rollback was called. Regarding Dataset: %s" %
                            self.get_dataset_name())
