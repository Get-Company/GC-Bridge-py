from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
import datetime


class ERPNestedDatasetObjectEntity(ERPDatasetObjectEntity):

    def __init__(self,
                 erp_obj,
                 dataset_name,
                 dataset_id_field,
                 dataset_id_value,
                 dataset_range,
                 nested_dataset_name,
                 nested_dataset_id_field,
                 nested_dataset_id_value,
                 nested_dataset_range,
                 prefill_json_directory
                 ):

        """ Needed attributes """
        self.is_nested = True
        self.nested_dataset_name = nested_dataset_name
        self.nested_dataset_id_field = nested_dataset_id_field
        self.nested_dataset_id_value = nested_dataset_id_value
        self.nested_dataset_range = nested_dataset_range
        self.nested_datasets = dict()
        self.nested_datasets_fields_list = dict()

        """ Call super class for all NOT nested """
        super().__init__(
            erp_obj=erp_obj,
            dataset_name=dataset_name,
            dataset_id_field=dataset_id_field,
            dataset_id_value=dataset_id_value,
            dataset_range=dataset_range,
            prefill_json_directory=prefill_json_directory
        )

        """ Now all datasets are created. Parent and Child """
        self.nested_datasets[self.nested_dataset_name] = self.created_dataset.NestedDataSets(self.nested_dataset_name)
        self.nested_datasets_fields_list[self.nested_dataset_name] = ""

        """ Lets check if we have parameters set Range or id"""
        # Range check
        if self.nested_dataset_range:
            # Get start and end
            self.nested_dataset_range_start = self.nested_dataset_range[0]
            self.nested_dataset_range_end = self.nested_dataset_range[1]

            # Ok now set the range
            self.set_nested_range(self.nested_dataset_range_start, self.nested_dataset_range_end)

        elif self.nested_dataset_id_field and self.nested_dataset_id_value:
            self.set_nested_dataset_cursor_to_field_value()

        # None dataset check
        else:
            pass

    def set_nested_(self, field):
        """
        Check the list self.nested_datatsets_fields_list whether e field is already in the list
        :param field:
        :return:
        """
        value = self.helper_get_value_of(field=field, dataset=self.nested_datasets[self.nested_dataset_name])
        self.nested_datasets_fields_list = {
            self.nested_dataset_name: {
                field: value
            }
        }
        return True

    def get_(self, field):
        """
        Check the list self.nested_datatsets_fields_list whether e field is already in the list. If not
        call the set_function, to set the field. Then return the value of the field
        :param field: string,int depending on the field
        :return: Value of the field
        """
        self.set_nested_(field)

        return self.nested_datasets_fields_list[self.nested_dataset_name][field]

    def set_is_nested(self, nested=True):
        self.is_nested = nested

    def get_is_nested(self):
        return self.is_nested

    def set_nested_dataset_name(self, nested_dataset_name):
        self.nested_dataset_name = nested_dataset_name

    def get_nested_dataset_name(self):
        return self.nested_dataset_name

    def get_nested_datasets(self):
        return self.nested_datasets

    def count_nested_datasets(self):
        return len(self.nested_datasets.keys())

    """ Positioning/Finding/Filtering """

    def set_nested_dataset_cursor_to_field_value(self):
        self.nested_datasets[self.nested_dataset_name].FindKey(self.nested_dataset_id_field,
                                                               self.nested_dataset_id_value)

    """ Range """

    def set_nested_range(self, start, end=None, field=None):
        if field is None:
            field = self.nested_dataset_id_field

        # Check if range is date
        if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
            self.nested_datasets[self.nested_dataset_name].SetRange(
                field,
                str(start.strftime("%d.%m.%Y %H:%M:%S")),
                str(end.strftime("%d.%m.%Y %H:%M:%S"))
            )
        else:
            self.nested_datasets[self.nested_dataset_name].SetRange(field, start, end)
        # Apply Range
        self.nested_datasets[self.nested_dataset_name].ApplyRange()
        # Check if we get results
        if self.range_count() == 0:
            print("Nothing in given range", start, end)
            return False

        # set the cursor to the first entry
        else:
            print("Found", self.range_count(), "Entries between", start, end)
        self.nested_datasets[self.nested_dataset_name].First()
        return True

    def range_next(self):
        self.nested_datasets[self.nested_dataset_name].Next()

    def range_first(self):
        self.nested_datasets[self.nested_dataset_name].First()

    def range_eof(self):
        """
        Checks if the end of the table/range is reached and returns True.
        :return: Bool
        """
        return self.nested_datasets[self.nested_dataset_name].Eof

    def range_count(self):
        return self.nested_datasets[self.nested_dataset_name].RecordCount

    def is_ranged(self):
        return self.nested_datasets[self.nested_dataset_name].IsRanged()
