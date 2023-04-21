import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
from datetime import datetime, timedelta
import calendar


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

    def set_special_price(self, start_date, price=None, percentage=None):
        self.edit_()
        if percentage:
            price = self.get_("Vk0.Preis") * (1-percentage/100)
            # Formatieren des Preises im deutschen Format
            price = '{:,.2f}'.format(price).replace(',', ' ').replace('.', ',').replace(' ', '.')

            print("Preis:", price)
        end_of_next_month_after_start_date = datetime(start_date.year, start_date.month + 2, 1) - timedelta(days=1)

        print("End of next month", end_of_next_month_after_start_date)
        self.update_("Vk0.SVonDat", start_date)
        self.update_("Vk0.SBisDat", end_of_next_month_after_start_date)
        self.update_("Vk0.SPr", price)
        self.update_("Vk1.SVonDat", start_date)
        self.update_("Vk1.SBisDat", end_of_next_month_after_start_date)
        self.update_("Vk1.SPr", price)

        self.post_()

