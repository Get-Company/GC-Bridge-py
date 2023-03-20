"""
Examples:

    # get Adress with AdrNr 10026
    adresse = ERPAdressenEntity(erp_obj=erp_obj, id_value='10026')
    print(adresse.get_('AdrNr'))

    # Get Range WShopID from 13470 - 13480
    adressen_range = ERPAdressenEntity(erp_obj=erp_obj, dataset_range=['13470', '13480', 'WShopID'])
    print("Is Ranged?:", adressen_range.is_ranged(), ' - ', adressen_range.range_count())
    print(adressen_range.get_('AdrNr'))
    adressen_range.range_next()
    print(adressen_range.get_('AdrNr'))

    # New Customer
    new_adress = ERPAdressenEntity(erp_obj=erp_obj)
    new_adress.create_new_customer()

    # Update fields
    adresse.edit_()
    adresse.update_("WShopAdrKz", 1)
    adresse...
    adresse.post_()

    # Search in Index fields
    Anschriften:
    Index: AdrNrAnsNr - Adressnummer
        IndexField:AdrNr - Adressnummer
        IndexField:AnsNr - Anschriftennummer1
    Index: 'AdrNrAnsNr', [Indexfield1: AdrNr, Indexfield2: AnsNr]
    Beispiel:
    anschriften_ntt.find_('AdrNrAnsNr', [self.get_('AdrNr'), self.get_('LiAnsNr')])

    Ansprechpartner:


"""
import csv
import logging
import re
from pprint import pprint

from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from datetime import datetime


class ERPAdressenEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'Adressen'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = str(id_value)  # Needs to be a string
        self.dataset_range = dataset_range

        self.prefill_json_directory = "main/src/json/customer/"
        self.skip_gspkz = True

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            prefill_json_directory=self.prefill_json_directory,
            skip_gspkz=self.skip_gspkz
        )

    def set_created_dataset(self):
        """
        Get the content of the fields by calling CreateDatasetEx(). All related tables are included
        :return:
        """
        self.created_dataset = self.get_dataset_infos().CreateDataSetEx()

    """ Overrides """

    def range_first(self):
        self.created_dataset.First()
        self.range_skip_gspkz()
        self.range_skip_email()

    def range_next(self):
        self.created_dataset.Next()
        self.range_skip_gspkz()
        self.range_skip_email()

    """ Sync Queries """

    def get_all_since_last_sync(self, last_sync_date):
        current_time = datetime.now()
        self.set_range(start=last_sync_date, end=current_time, field="LtzAend")
        return True

    """ Create and Update Customer """

    def update_customer(self, update_fields_list):
        self.edit_()
        for field_key, field_value in update_fields_list.items():
            # print("Set", field_key,":", field_value)
            self.create_(field_key, field_value)

        self.set_updated_fields(updated_at=update_fields_list["LtzAend"])
        self.post_()

    def create_new_customer(self, bridge_customer, customer_file=None):
        """
        Complete function for creating a new customer.
        Just add a dict of fields, and give the
        path to the prefill file.
        """
        # Create the new dataset
        self.create_dataset()

        # Append new row
        self.append_()

        # Next free AdrNr
        adrnr = self.get_next_free_adrnr()
        print("This AdrNr is reserved:", adrnr)
        self.create_("AdrNr", adrnr)

        # Fields from the Entity
        fields = bridge_customer.map_db_to_erp()
        for field_key, field_value in fields.items():
            self.create_(field_key, field_value)

        # Fill out the fields given rom the json file
        self.prefill_from_file(file=self.prefill_json_directory + customer_file)

        self.post_()

        for address in bridge_customer.addresses:

            # Create a Dataset for Anschrift
            erp_anschrift = ERPAnschriftenEntity(erp_obj=self.erp_obj)
            erp_anschrift.create_dataset()

            # Append new row
            erp_anschrift.append_()

            # Fields from the Entity
            erp_anschrift.create_("AdrNr", adrnr)
            fields_anschrift = address.map_db_to_erp_anschrift()

            for field_anschrift_key, field_anschrift_value in fields_anschrift.items():
                erp_anschrift.create_(field_anschrift_key, field_anschrift_value)

            erp_anschrift.post_()

            # Create Dataset for Ansprechpartner
            erp_ansprechpartner = ERPAnsprechpartnerEntity(erp_obj=self.erp_obj)
            erp_ansprechpartner.create_dataset()

            # Append new row
            erp_ansprechpartner.append_()

            # Fields from the entity
            erp_ansprechpartner.create_("AdrNr", adrnr)
            erp_ansprechpartner.create_("AnsNr", address.erp_ansnr)
            erp_ansprechpartner.create_("AspNr", address.erp_aspnr)
            erp_ansprechpartner.create_("StdKz", 1)
            erp_ansprechpartner.create_("Anr", "Frau")
            erp_ansprechpartner.create_("VNa", address.first_name)
            erp_ansprechpartner.create_("NNa", address.last_name)

            # fields_ansprechpartner = address.map_db_to_erp_ansprechpartner()
            # for field_ansprechpartner_key, field_ansprechpartner_value in fields_ansprechpartner.items():
            #     erp_ansprechpartner.create_(field_ansprechpartner_key, field_ansprechpartner_value)

            erp_ansprechpartner.post_()

        customer_info = {
            "adrnr": adrnr,
            "erp_ltz_aend": self.get_("LtzAend")
        }

        return customer_info

    """ Special Queries """

    def range_skip_email(self):
        while True:
            if self.get_login():
                break
            elif self.get_login() is False and not self.range_eof():
                self.range_next()

    def get_next_free_adrnr(self):
        return self.created_dataset.SetupNr("")

    def map_bridge_to_erp(self, bridge_entity):
        pass

    def remove_webshop_id(self):
        """ Easy remove when a client wants to have his account deleted """
        self.edit_()

        self.update_('WShopAdrKz', 0)
        self.update_("WShopID", "")

        print("After update:", self.get_("WShopAdrKz"), self.get_("WShopID"))

        self.post_()

    def add_webshop_id(self, webshop_id):
        self.edit_()

        self.update_('WShopAdrKz', 1)
        self.update_("WShopID", webshop_id)

        print("After update:", self.get_("WShopAdrKz"), self.get_("WShopID"))

        self.post_()

    def remove_amazon_id(self):
        """ Easy remove when a client wants to have his account deleted """

        self.edit_()

        self.update_("AucWebKz", False)
        self.update_("AucWebID", "")

        self.post_()

    def get_special_orgaplan_without_turnover(self):
        """ We want all customers from Orgaplan without a turnover"""
        # We are searching for SuchBegriff ORGCL
        self.set_range(start='ORGCL', end='ORGCL', field='SuchBeg')
        # Filter all by Erstumsatz > 1899 which is the standard value in büro+
        self.filter_expression("ErstUmsDat<'31.12.1900'")
        # Set the filter and set to first query of range
        self.filter_set()
        self.range_first()

    def get_special_orgaplan_with_turnover(self):
        """ We want all customers from Orgaplan without a turnover"""
        # We are searching for SuchBegriff ORGCL
        self.set_range(start='ORGCL', end='ORGCL', field='SuchBeg')
        # Filter all by Erstumsatz > 1899 which is the standard value in büro+
        self.filter_expression("ErstUmsDat>'31.12.1900'")
        # Set the filter and set to first query of range
        self.filter_set()
        self.range_first()

    def get_special_standard_anschriften_and_ansprechpartner(self):
        """
        Returns a dict of all necessary fields from anschriften and ansprechpartner
        anschriften
            ['shipping']
                ['anschrift']
                    ['Na1'], ['Na2'], ['Na3']
                ['ansprechpartner']
                    ['Anr'], ['VNa'], ['NNa']
            ['invoice']
                ['anschrift']
                    ['Na1'], ['Na2'], ['Na3']
                ['ansprechpartner']
                    ['Anr'], ['VNa'], ['NNa']
        This function gets the standard fields from LiAnsNr and ReAnsNr and returns it in a dict
        :return: dict anschriften
        """
        anschriften_ntt = ERPAnschriftenEntity(erp_obj=self.erp_obj)
        anschriften_ntt.find_('AdrNrAnsNr', [self.get_('AdrNr'), self.get_('LiAnsNr')])
        ansprechpartner_ntt = ERPAnsprechpartnerEntity(erp_obj=self.erp_obj)

        ansprechpartner_ntt.find_('AdrNrAnsNrAspNr',
                                  [self.get_('AdrNr'), self.get_('LiAnsNr'), anschriften_ntt.get_('AspNr')])

        # Shipping
        anschriften = {
            'shipping': {
                'anschrift': {
                    'Na1': anschriften_ntt.get_('Na1'),
                    'Na2': anschriften_ntt.get_('Na2'),
                    'Na3': anschriften_ntt.get_('Na3'),
                },
                'ansprechpartner': {
                    'Anr': ansprechpartner_ntt.get_('Anr'),
                    'VNa': ansprechpartner_ntt.get_('VNa'),
                    'NNa': ansprechpartner_ntt.get_('NNa'),
                }
            }
        }

        # Invoice
        anschriften_ntt.find_('AdrNrAnsNr', [self.get_('AdrNr'), self.get_('ReAnsNr')])
        ansprechpartner_ntt.find_('AdrNrAnsNrAspNr',
                                  [self.get_('AdrNr'), self.get_('ReAnsNr'), anschriften_ntt.get_('AspNr')])

        anschriften['invoice'] = {
            'anschrift': {
                'Na1': anschriften_ntt.get_('Na1'),
                'Na2': anschriften_ntt.get_('Na2'),
                'Na3': anschriften_ntt.get_('Na3')
            },
            'ansprechpartner': {
                'Anr': ansprechpartner_ntt.get_('Anr'),
                'VNa': ansprechpartner_ntt.get_('VNa'),
                'NNa': ansprechpartner_ntt.get_('NNa'),
            }
        }

        return anschriften

    def get_anschriften(self):
        anschriften_ntt = ERPAnschriftenEntity(erp_obj=self.erp_obj)
        anschriften_ntt.set_range(field='AdrNrAnsNr', start=self.get_('AdrNr'))
        anschriften_ntt.range_first()
        return anschriften_ntt

    def get_special_standard_billing_address(self):
        """
        Get the standard billing address
        :return: obj ERPAnschriftenEntity
        """
        anschriften_ntt = ERPAnschriftenEntity(erp_obj=self.erp_obj)
        anschriften_ntt.find_('AdrNrAnsNr', [self.get_('AdrNr'), self.get_('ReAnsNr')])

        return anschriften_ntt

    def get_special_standard_shipping_address(self):
        """
        Get the standard billing address
        :return: obj ERPAnschriftenEntity
        """
        anschriften_ntt = ERPAnschriftenEntity(erp_obj=self.erp_obj)
        anschriften_ntt.find_('AdrNrAnsNr', [self.get_('AdrNr'), self.get_('LiAnsNr')])

        return anschriften_ntt

    def get_login(self):
        """
        This function returns the email address of the special standard billing address.
        If the email address is not available, it returns False.

        Returns:
            str or bool: email address or False if not available
        """
        address = self.get_special_standard_billing_address()
        email = address.get_("EMail1")
        # Check if the email address exists and if it is valid
        if email and re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return email
        else:
            return False

    def print_dataset_fields(self):

        super().print_dataset_fields()

    def print_dataset_indices(self):
        super().print_dataset_indices()

    def set_field_by_csv(self):
        """ Insert a csv with field - values """
        import csv
        with open('main/src/csv/s_user_right.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';')
            next(csvreader)  # Überspringe die Kopfzeile
            for row in csvreader:
                erp_obj = None
                adressnummer, id_webshop, webshop_adresse_kennzeichen = row
                erp_address_entity = ERPAdressenEntity(erp_obj=erp_obj, id_value=adressnummer)
                if erp_address_entity:
                    print(erp_address_entity.get_("AdrNr"))
                    erp_address_entity.add_webshop_id(webshop_id=id_webshop)

        print("Fertit")
