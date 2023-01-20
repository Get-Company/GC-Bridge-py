import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
import datetime


class ERPHistoryEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'History'
        self.dataset_id_field = 'AdrNr'
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

    def get_history_from_product_by_date(self, artnr, start_date, end_date):
        """
        Asks the history DataSet for the History of a Product in a certain date-range
        :param artnr: "224816"
        :param start_date: "01.01.2019"
        :param end_date: "31.12.2022"
        :return: ERP Range Object
        """
        history_range = self.set_range(start=[artnr, start_date], end=[artnr, end_date], field="ArtNr")
        return history_range
