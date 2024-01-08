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

    def set_special_price(self, start_date,end_date=None, price=None, percentage=None):
        self.edit_()
        if percentage:
            price = self.get_("Vk0.Preis") * (1-percentage/100)
            # Formatieren des Preises im deutschen Format
            price = '{:,.2f}'.format(price).replace(',', ' ').replace('.', ',').replace(' ', '.')

            print("Preis:", price)
        if end_date is None:
            # Beware for the 11th and 12th month. We would have the 13th and 14th month,
            # thatswhy we subtract 12 Month from it

            end_date_year = start_date.year
            end_date_month = start_date.month + 2

            if end_date_month > 12:
                end_date_month -= 12
                end_date_year += 1

            end_date = datetime(end_date_year, end_date_month, 1) - timedelta(days=1)

        print("Startdate:", start_date, "End of the month after the next month:", end_date)
        self.update_("Vk0.SVonDat", start_date)
        self.update_("Vk0.SBisDat", end_date)
        self.update_("Vk0.SPr", price)
        self.update_("Vk1.SVonDat", start_date)
        self.update_("Vk1.SBisDat", end_date)
        self.update_("Vk1.SPr", price)

        self.post_()

    def reset_prices(self):
        self.edit_()

        self.update_("Vk0.SVonDat", "")
        self.update_("Vk0.SBisDat", "")
        self.update_("Vk0.SPr", 0)
        self.update_("Vk0.SRabKz", True)
        self.update_("Vk1.SVonDat", "")
        self.update_("Vk1.SBisDat", "")
        self.update_("Vk1.SPr", 0)
        self.update_("Vk1.SRabKz", True)

        self.post_()



