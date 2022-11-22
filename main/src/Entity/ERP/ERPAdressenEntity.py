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
        IndexField:AnsNr - Anschriftennummer
    Index: 'AdrNrAnsNr', [Indexfield1: AdrNr, Indexfield2: AnsNr]
    Beispiel:
    anschriften_ntt.find_('AdrNrAnsNr', [self.get_('AdrNr'), self.get_('LiAnsNr')])

    Ansprechpartner:


"""
import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
import datetime


class ERPAdressenEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'Adressen'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = str(id_value)  # Needs to be a string
        self.dataset_range = dataset_range

        self.prefill_json_directory = "main/src/json/customer/"

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            prefill_json_directory=self.prefill_json_directory
        )

    def set_created_dataset(self):
        """
        Get the content of the fields by calling CreateDatasetEx(). All related tables are included
        :return:
        """
        print("In Child! EX called")
        self.created_dataset = self.get_dataset_infos().CreateDataSetEx()

    def get_next_free_adrnr(self):
        return self.created_dataset.SetupNr("")

    def create_new_customer(self, file="webshop.yaml", fields=None):
        """
        Complete function for creating a new customer . Just add a dict of fields, and give the
        path to the prefill file.
        """
        # Create the new dataset
        self.create_dataset()
        # Append new row
        self.append_()
        # Fill out the fields given rom the json file
        self.prefill_from_file(file=self.prefill_json_directory+file)
        # Fill th fields given from the dict
        if fields:
            for field_key, field_value in fields.items():
                self.create_(field_key, field_value)
        # Set the next free AdressNr
        self.create_("AdrNr", self.get_next_free_adrnr())
        # Post everything
        self.post_()
        return True

    def remove_webshop_id(self):
        """ Easy remove when a client wants to have his account deleted """
        self.edit_()

        self.update_('WShopAdrKz', 0)
        self.update_("WShopID", "")

        print("After update:", self.get_("WShopAdrKz"), self.get_("WShopID"))

        self.post_()

    def remove_amazon_id(self):
        """ Easy remove when a client wants to have his account deleted """

        self.edit_()

        self.update_("AucWebKz", False)
        self.update_("AucWebID", "")

        self.post_()

    """ Special Queries """
    def get_special_orgaplan_without_turnover(self):
        """ We want all customers from Orgaplan without a turnover"""
        # We are searching for SuchBegriff ORGCL
        self.set_range(start='ORGCL', end='ORGCL', field='SuchBeg')
        # Filter all by Erstumsatz > 1899 which is the standard value in büro+
        self.filter_expression("ErstUmsDat<'31.12.1900'")
        # Set the filter and set to first query of range
        self.filter_set()
        self.range_first()

    """ Special Queries """

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

        ansprechpartner_ntt.find_('AdrNrAnsNrAspNr', [self.get_('AdrNr'), self.get_('LiAnsNr'), anschriften_ntt.get_('AspNr')])

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
        ansprechpartner_ntt.find_('AdrNrAnsNrAspNr', [self.get_('AdrNr'), self.get_('ReAnsNr'), anschriften_ntt.get_('AspNr')])

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

    def print_dataset_fields(self):
        super().print_dataset_fields()

    def print_dataset_indices(self):
        super().print_dataset_indices()

