"""
Examples:
    Get the standard shipping

"""
import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity

import datetime


class ERPAnschriftenEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'Anschriften'
        self.dataset_id_field = 'AdrNrAnsNr'  # Adressnummer
        self.dataset_id_value = id_value
        self.dataset_range = dataset_range

        self.prefill_json_directory = "main/src/json/customer_address/"

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            prefill_json_directory=self.prefill_json_directory
        )

    def get_ansprechpartner(self):
        ansprechpartner_ntt = ERPAnsprechpartnerEntity(erp_obj=self.erp_obj)
        ansprechpartner_ntt.set_range(field='AdrNrAnsNrAspNr', start=[self.get_("AdrNr"), self.get_("AnsNr")])
        ansprechpartner_ntt.range_first()
        return ansprechpartner_ntt

    """ Special Queries """
    def get_special_standard_address_fields(self):
        anschrift = {
            'Na1': self.get_('Na1'),
            'Na2': self.get_('Na2'),
            'Na3': self.get_('Na3')
        }
        return anschrift

    def get_country_name(self):
        country_name = self.get_("LandBez")
        return country_name

    def create_new_address(self, adrnr, ansnr,  customer_file=None, fields=None):
        """
        Complete function for creating a new customer_address .
        Just add a dict of fields, and give the
        path to the prefill file.
        """
        # Create the new dataset
        self.create_dataset()

        # Append new row
        self.append_()

        # Fill out the fields given rom the json file
        if customer_file:
            self.prefill_from_file(file=self.prefill_json_directory+customer_file)
        # Fill th fields given from the dict
        if fields:
            for field_key, field_value in fields.items():
                self.create_(field_key, field_value)
        self.create_("AdrNr", adrnr)
        self.create_("AnsNr", adrnr)

        # Post everything
        self.post_()

    def update_address(self, update_fields_list):
        self.edit_()

        for field_key, field_value in update_fields_list.items():
            # print("Set", field_key,":", field_value)
            self.create_(field_key, field_value)

        self.post_()



