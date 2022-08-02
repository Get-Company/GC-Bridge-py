import datetime
import logging
import string
import json
import yaml


from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity
from main.src.Repository.functions_repository import parse_a_date


class ERPDatasetObjectEntity(object):
    """
    This is the Parent class of all Datasets from Büro+. Initiate it with an ERPConnectionEntity,
    the datasets name it's id field and the id (value)

    Field Types:
    If a field isn't recognized, add it to the field_types dict

    CRUD:
    When changing/creating aso something. be sure to call self.commit() afterwards to make the changes happen
    """

    def __init__(self,
                 erp_obj,
                 dataset_name,
                 dataset_id_field,
                 dataset_id_value,
                 dataset_range,
                 prefill_json_directory
                 ):

        """ Needed attributes """
        self.erp_obj = erp_obj
        self.created_dataset = None
        self.dataset_infos = None
        self.dataset = None
        self.dataset_name = dataset_name
        self.dataset_id_field = dataset_id_field
        self.dataset_id_value = dataset_id_value
        self.dataset_fields = dict()
        self.nested_datasets = dict()
        """ For the templates for customers, orders aso. Is filled in the child """
        self.prefill_json_directory = prefill_json_directory
        """ Dict FieldTypes and their translation/mapping """
        self.field_types = {
            'WideString': 'AsString',
            'Float': 'AsFloat',
            'Blob': 'Text',
            'Date': 'AsDatetime',
            'DateTime': 'AsDatetime',
            'Integer': 'AsInteger',
            'Boolean': 'AsBoolean',
            'Byte': 'AsInteger'

        }
        """ The fields of the dataset and their values """
        self.fields_list = dict()

        """ These functions must be called for creating the dataset """
        self.set_dataset_infos()    # <-----|
        #                                   |-- Creating the Dataset!!
        self.set_created_dataset()  # <-----|

        """ Check the parameter if we need to 1 a range or none """
        # Range check
        if dataset_range:  # Check iwe got a range and then set start and end
            self.dataset_range_start = dataset_range[0]
            self.dataset_range_end = dataset_range[1]

            # Set the id field, if given. ex: AdrNr in Adresse
            if dataset_range[2]:
                self.set_dataset_id_field(dataset_range[2])

            # OK now set the range
            self.set_range(self.dataset_range_start, self.dataset_range_end)

            # Check for nested datasets
            # Since we use CreateDataSetEx, we have all realted dbs included!
            # Delete - not used since 27.07.2022?
            # self.set_nested_datasets()  # Read the nested datasets

        # One dataset check
        elif self.dataset_id_field and self.dataset_id_value:  # Check if we got field and value for a search
            self.set_dataset_cursor_to_field_value()  # Find the given Field and Value
            # Check for nested datasets
            # Since we use CreateDataSetEx, we have all realted dbs included!
            # Delete - not used since 27.07.2022?
            # self.set_nested_datasets()  # Read the nested datasets

        # None check
        else:
            # No need to do anything
            pass

    def __repr__(self):
        for k, v in self.fields_list.items():
            print(str(v))

    """ CRUD Actions - set_, get_, update_, delete_ """
    def set_(self, field):
        """
        The field is collected and stored in a list.
        ! Important: Use the field names as used in Büro+
        Set the field ex: set_('ArtNr'). The helper method reads the field type,
        translates it as ex. 'AsString' and adss it to the dict.
        :param field: string Ex 'ArtNr' on Artikel
        :return:
        """
        self.fields_list[field] = self.helper_get_value_of(field)
        return True

    def get_(self, field):
        """
        If the field isn't in the fields_list dict OR we have a range - the field must be set again, with the new
        properties.
        ! Important: Use the field names as used in Büro+
        Access the field dict(). Ex: get_('ArtNr'). The dict() is read and the value is returned.
        :param field: string Ex 'ArtNr' on Artikel
        :return: dict self.fields_list
        """
        if field not in self.fields_list or self.is_ranged():
            self.set_(field)

        return self.fields_list[field]

    def update_(self, field, value):
        """
        The dataset is put in Edit() Mode. The list is updated and the field is forwarded to the helper
        which updates the field in büro+
        ! Important: Use the field names as used in Büro+
        :param field: string Ex 'ArtNr' on Artikel
        :param value: string the value for the field
        :return: dict self.fields_list
        """
        self.edit_()
        self.fields_list[field] = value
        self.helper_set_value_of(field, value)

    def create_(self, field, value):
        self.fields_list[field] = value
        self.helper_set_value_of(field, value)

    def delete_(self, check_delete=True):
        self.edit_()
        if check_delete:
            self.delete_check_dataset()
        else:
            self.delete_dataset()

        self.post_dataset()

    def copy_(self):
        """ Child classes need to take care of this """
        pass

    def edit_(self):
        """ To edit a give dataset """
        self.startTransaction()
        self.created_dataset.Edit()

    def append_(self):
        """ To create a Dataset """
        self.startTransaction()
        self.created_dataset.Append()

    def startTransaction(self):
        """ the table is locked until commit!"""
        self.created_dataset.StartTransaction()

    def delete_dataset(self):
        self.created_dataset.Delete()

    def delete_check_dataset(self):
        """
        This can be used to check whether the selected record should be deleted. The user is shown a separate
        window with queries about this deletion process.
        """
        self.created_dataset.CheckDelete(True, True)

    def post_dataset(self):
        try:
            self.created_dataset.Post()
            self.created_dataset.Commit()
        except:
            self.created_dataset.RollBack()
            self.created_dataset.Cancel()
            logging.warning("Post/Commit could not execute. Rollback was called. Regarding Dataset: %s" %
                            self.get_dataset_name())

    """ ERP """
    def set_erp_obj(self, erp_obj: object):
        self.erp_obj = erp_obj

    """ Dataset """
    def create_dataset(self):
        """ This function must be called when this object is created but with no id_value """
        self.set_dataset_infos()

    def set_dataset_name(self, dataset_name):
        self.dataset_name = dataset_name

    def get_dataset_name(self):
        return self.dataset_name

    def set_dataset_id_field(self, dataset_id_field):
        self.dataset_id_field = dataset_id_field

    def get_dataset_id_field(self):
        return self.dataset_id_field

    def set_dataset_id_value(self, dataset_id_value):
        self.dataset_id_value = dataset_id_value

    def get_dataset_id_value(self):
        return self.dataset_id_value

    def set_dataset(self, dataset):
        """
        Thiis function is to set the dataset after FindKey() or SetRange(). We got the dataset
        but we set the cursor to the field we need.
        :param dataset:
        :return:
        """
        self.dataset = dataset

    def get_dataset(self):
        return self.dataset

    def set_dataset_infos(self):
        self.dataset_infos = self.erp_obj.get_erp().DataSetInfos.Item(self.dataset_name)

    def get_dataset_infos(self):
        return self.erp_obj.get_erp().DataSetInfos.Item(self.dataset_name)

    def set_dataset_fields(self):
        """
        Makes a list of all fields of the given dataset.
        Example: Get the Field (not the value) ArtNr from Dataset Artikel:
            fields = get_dataset_fields()
            print(fields.['ArtNr'])
        :return:
        """
        for field in self.erp_obj.get_erp().DatasetInfos.Item(self.dataset_name).Fields:
            new_field = {
                field.Name: {
                    "Name": field.Name,
                    "Info": field.Info,
                    "Type": field.FieldType
                }
            }
            self.dataset_fields.update(new_field)

    def get_dataset_fields(self):
        return self.dataset_fields

    def set_created_dataset(self):
        """
        Get the content of the fields by calling CreateDataset()
        :return:
        """
        self.created_dataset = self.get_dataset_infos().CreateDataSetEx()

    def get_created_dataset(self):
        return self.created_dataset

    """ Nested datasets """
    def set_nested_datasets(self):
        for nested in self.get_created_dataset().NestedDataSets:
            self.nested_datasets[nested.Name] = nested

    def get_nested_datasets(self):
        return self.nested_datasets

    def get_nested_dataset(self, nested_dataset_name):
        return self.nested_datasets[nested_dataset_name]

    def count_nested_datasets(self):
        return len(self.nested_datasets.keys())

    """ Positioning/Finding/Filtering """
    def set_dataset_cursor_to_field_value(self):
        self.created_dataset.FindKey(self.dataset_id_field, self.dataset_id_value)

    def find_(self, field=None, value=None):
        """
        Just find by standard field and value ex: Artikel field='ArtNr', value='204116'
        or find with the given field and value
        :param field: str the field for the search
        :param value: str the value for the field to search
        :return: None
        """
        if field:
            self.set_dataset_id_field(field)
        if value:
            self.set_dataset_id_value(value)

        self.set_dataset_cursor_to_field_value()


    """ Range """
    def set_range(self, start, end, field=None):
        # field is ex: 'Adrnr' could be different when calling the function directly
        if not field:
            field = self.dataset_id_field
        # Check if range is date
        if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
            self.created_dataset.SetRange(
                field,
                str(start.strftime("%d.%m.%Y %H:%M:%S")),
                str(end.strftime("%d.%m.%Y %H:%M:%S"))
            )
        else:
            self.created_dataset.SetRange(field, start, end)
        # Apply Range
        self.created_dataset.ApplyRange()
        # Check if we get results
        if self.range_count() == 0:
            raise IndexError("Nothing in given range", start.strftime("%d.%m.%Y %H:%M:%S"), end.strftime("%d.%m.%Y %H:%M:%S"))
        # set the cursor to the first entry
        self.created_dataset.First()

    def range_next(self):
        self.created_dataset.Next()

    def range_last(self):
        self.created_dataset.Last()

    def range_count(self):
        return self.created_dataset.RecordCount

    def is_ranged(self):
        return(self.created_dataset.IsRanged())

    """ Helper """
    def helper_get_value_of(self, field):
        """
        Eval interprets a string as code.
        Example: We get AsString from field_types dict and add it to 'self.dataset.Fields.Item(str(field)).'
        Therefore we get 'self.dataset.Fields.Item(str(field)).AsString' which gives us the right field value
        Make sure all fields are in the dict
        :param field:
        :return:
        """
        field_type = self.created_dataset.Fields.Item(field).FieldType
        if field_type in self.field_types:
            print("Read %s as %s" % (field, self.field_types[field_type]))
            return eval('self.created_dataset.Fields.Item(str(field)).' + self.field_types[field_type])
        else:
            print("We got the not known Type '%s' for field '%s' " % (field_type, field))
            return False

    def helper_set_value_of(self, field, value):
        """
        Eval interprets a string as code.
        Example: We get AsString from field_types dict and add it to 'self.dataset.Fields.Item(str(field)).'
        Therefore we get 'self.dataset.Fields.Item(str(field)).AsString = "VALUE"' which gives us the right field value
        Make sure all fields are in the dict
        :param field: string Field name after büro+ convention
        :param value: new value
        :return:
        """
        field_type = self.created_dataset.Fields.Item(field).FieldType
        if field_type in self.field_types:
            print("Set %s as %s" % (field, self.field_types[field_type]))
            return exec('self.created_dataset.Fields("' +
                        str(field) +
                        '").' +
                        self.field_types[field_type] +
                        " = '" +
                        str(value) +
                        "'")
        else:
            print("We got the not known Type '%s' for field '%s' " % (field_type, field))
            return False

    """ New Dataset """
    def prefill_from_file(self, file=None):
        if not file:
            raise FileNotFoundError
        else:
            with open(self.prefill_json_directory + file, 'r') as f:
                print("Open file for prefill: ", self.prefill_json_directory + file)
                # data = json.load(f)
                try:
                    data = yaml.safe_load(f)
                    for key, value in data.items():
                        print("Creating fields for prefill:", key, value)
                        self.create_(key, value)
                except yaml.YAMLError as exc:
                    print(exc)

