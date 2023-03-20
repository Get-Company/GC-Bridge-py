
import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
import datetime


class ERPAnsprechpartnerEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'Ansprechpartner'
        self.dataset_id_field = 'AdrNrAnsNrAspNr'
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

    def create_new_contact(self, adrnr, ansnr, aspnnr, customer_file=None, fields=None):
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
        self.create_("AnsNr", ansnr)
        self.create_("AspNr", aspnnr)

        # Post everything
        self.post_()

    def update_contact(self, update_fields_list):
        self.edit_()

        for field_key, field_value in update_fields_list.items():
            # print("Set", field_key,":", field_value)
            self.create_(field_key, field_value)

        self.post_()


