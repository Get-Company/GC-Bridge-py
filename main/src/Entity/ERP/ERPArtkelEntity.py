import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
import datetime


class ERPArtikelEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'Artikel'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = id_value
        self.dataset_range = dataset_range
        self.prefill_json_directory = None

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            prefill_json_directory=self.prefill_json_directory
        )

    """ Special Queries """
    def get_einheit(self):
        self.find_(value=self.dataset_id_value)
        print("Get Einheit:", self.get_('Einh'))
        return self.get_('Einh')

    def get_artkel_nummer(self):
        return self.get_('ArtNr')

    def get_title(self):
        return self.get_('Bez1')

