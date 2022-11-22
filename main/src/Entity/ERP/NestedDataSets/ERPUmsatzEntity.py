from main.src.Entity.ERP.NestedDataSets.ERPNestedDatasetObjectEntity import ERPNestedDatasetObjectEntity

"""
Attention: NestedDataSet
Umsatz is the NestedDataSet from Adressen and its called Ums (yes Ums)
We have to set the NestedDataSet as the Created Dataset in this class to get all the functions
Have a look at"""


class ERPUmsatzEntity(ERPNestedDatasetObjectEntity):

    def __init__(self, erp_obj, adrnr, nested_dataset_id_value=None, nested_dataset_range=None):
        self.erp_obj = erp_obj

        """ Parent """
        self.dataset_name = 'Adressen'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = adrnr
        self.dataset_range = None

        """ Nested """
        self.nested_dataset_name = 'Ums'
        self.nested_dataset_id_field = 'Jahr'
        self.nested_dataset_id_value = nested_dataset_id_value
        self.nested_dataset_range = nested_dataset_range
        self.prefill_json_directory = None

        """ Functions before the supper INIT"""
        self.set_is_nested(True)

        if nested_dataset_id_value:
            self.set_nested_range(start=nested_dataset_id_value, field=self.nested_dataset_id_field)

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            nested_dataset_name=self.nested_dataset_name,
            nested_dataset_id_field=self.nested_dataset_id_field,
            nested_dataset_id_value=self.nested_dataset_id_value,
            nested_dataset_range=self.nested_dataset_range,
            prefill_json_directory=self.prefill_json_directory

        )
