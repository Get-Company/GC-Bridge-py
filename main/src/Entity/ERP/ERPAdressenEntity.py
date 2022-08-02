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

"""
import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
import datetime


class ERPAdressenEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'Adressen'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = id_value
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

    """ Functions specific to this entity """
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
        self.post_dataset()
        return True

    def remove_webshop_id(self):
        """ Easy remove when a clients wants to have his account deleted """
        self.edit_()

        self.update_('WShopAdrKz', False)
        self.update_("WShopID", "")

        self.post_dataset()

    def remove_amazon_id(self):
        """ Easy remove when a clients wants to have his account deleted """

        self.edit_()

        self.update_("AucWebKz", False)
        self.update_("AucWebID", "")

        self.post_dataset()




