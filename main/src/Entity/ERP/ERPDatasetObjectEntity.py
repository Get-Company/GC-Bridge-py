import datetime
import logging
import string
import json
from pprint import pprint

import yaml

# Tools
from main.src.Repository.functions_repository import find_image_filename_in_path


class ERPDatasetObjectEntity(object):
    """
    This is the Parent class of all Datasets from Büro+. Initiate it with an ERPConnectionEntity,
    the datasets name its id field and the id (value)

    Field Types:
    If a field isn't recognized, add it to the field_types dict

    CRUD:
    When changing/creating aso something. be sure to call self.commit() afterwards to make the changes happen

    Creating the dataset manually these two functions need to be called:
    self.set_dataset_infos()  # <-----|
    #                                   |-- Creating the Dataset!!
    self.set_created_dataset()  # <-----|

    """

    def __init__(self,
                 erp_obj,
                 dataset_name,
                 dataset_id_field,
                 dataset_id_value,
                 dataset_range,
                 prefill_json_directory,
                 skip_gspkz = True,
                 ):
        self.erp_obj = erp_obj
        self.created_dataset = None
        self.dataset_infos = None
        self.dataset = None
        self.dataset_name = dataset_name
        self.dataset_id_field = dataset_id_field
        self.dataset_id_value = dataset_id_value
        self.dataset_fields = dict()
        """ For the templates for customers, orders aso. Is filled in the child """
        self.prefill_json_directory = prefill_json_directory
        """ If the dataset is blocked """
        self.skip_gspkz = skip_gspkz
        """ Dict FieldTypes and their translation/mapping """
        self.field_types = {
            'WideString': 'AsString',
            'Float': 'AsFloat',
            'Blob': 'Text',
            'Date': 'AsDatetime',
            'DateTime': 'AsDatetime',
            'Integer': 'AsInteger',
            'Boolean': 'AsInteger',  # AsBoolean: True/False | AsInteger: 1/0
            'Byte': 'AsInteger',
            'Info': 'Text',
            'String': 'AsString',
            'Double': 'AsString'

        }
        self.field_types_to_set = {
            'WideString': 'AsString',
            'Float': 'AsFloat',
            'Blob': 'Text',
            'Date': 'AsString',
            'DateTime': 'AsString',
            'Integer': 'AsInteger',
            'Boolean': 'AsInteger',  # AsBoolean: True/False | AsInteger: 1/0
            'Byte': 'AsInteger',
            'Info': 'Text',
            'String': 'AsString',
            'Double': 'AsString'

        }
        """ The fields of the dataset and their values """
        self.fields_list = dict()

        """ These functions must be called for creating the dataset """
        self.set_dataset_infos()  # <-----|
        #                                   |-- Creating the Dataset!!
        self.set_created_dataset()  # <-----|

        """ Check the parameter if we need to 1 a range or none """
        # Range check
        if dataset_range:  # Check iwe got a range and then set start and end
            self.dataset_range_start = dataset_range[0]
            self.dataset_range_end = dataset_range[1]

            # OK now set the range
            self.set_range(self.dataset_range_start, self.dataset_range_end)

        # One dataset check
        elif self.dataset_id_field and self.dataset_id_value:  # Check if we got field and value for a search
            self.set_dataset_cursor_to_field_value()  # Find the given Field and Value

        # None check
        else:
            # No need to do anything
            pass

    def __repr__(self):
        return "Entity: %s, %s: %s" % (self.dataset_name, self.dataset_id_field, self.dataset_id_value)

    def __del__(self):
        print(f"Object {self.dataset_name} destroyed")

    """ CRUD Actions - set_, get_, update_, delete_ """

    def set_(self, field):
        """
        The field is collected and stored in a list.
        ! Important: Use the field names as used in Büro+
        Set the field ex: set_('ArtNr'). The helper method reads the field type,
        translates it as ex. 'AsString' and adds it to the dict.
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
        # Todo: If ranged! Do we need a list of all ranged fields?
        It checks the list fields_list if the field is given. The first item of range sets the field. So it is not
        called again for the whole range. Every item after the first won't be set!

        if field not in self.fields_list:
        """
        # field = 'AdrNr'
        self.set_(field)
        return self.fields_list[field]

    def get_images(self):
        """
        Gets the images by the Special COM Query GetEditObject(4).LinkFilename
        Removes the path
        splits the image_file into name and type
        :return: array with objects image.name, image.type
        # Todo: Make it nicer and maybe use DataSet: Bilder ?
        """
        dataset = self.get_created_dataset()
        images = []

        image_path = dataset.Fields.Item("Bild").GetEditObject(4).LinkFileName
        if image_path:
            image_file = find_image_filename_in_path(image_path)
            image_array = image_file.split('.', 1)

            images.append(
                {"name": image_array[0],
                 "type": image_array[1],
                 "order": 1,
                 }
            )
        else:
            pass

        image_path = dataset.Fields.Item("Bild2").GetEditObject(4).LinkFileName
        if image_path:
            image_file = find_image_filename_in_path(image_path)
            image_array = image_file.split('.', 1)

            images.append(
                {"name": image_array[0],
                 "type": image_array[1],
                 "order": 2,
                 }
            )
        else:
            pass

        image_path = dataset.Fields.Item("Bild3").GetEditObject(4).LinkFileName
        if image_path:
            image_file = find_image_filename_in_path(image_path)
            image_array = image_file.split('.', 1)

            images.append(
                {"name": image_array[0],
                 "type": image_array[1],
                 "order": 3,
                 }
            )
        else:
            pass

        image_path = dataset.Fields.Item("Bild4").GetEditObject(4).LinkFileName
        if image_path:
            image_file = find_image_filename_in_path(image_path)
            image_array = image_file.split('.', 1)

            images.append(
                {"name": image_array[0],
                 "type": image_array[1],
                 "order": 4,
                 }
            )
        else:
            pass

        image_path = dataset.Fields.Item("Bild5").GetEditObject(4).LinkFileName
        if image_path:
            image_file = find_image_filename_in_path(image_path)
            image_array = image_file.split('.', 1)

            images.append(
                {"name": image_array[0],
                 "type": image_array[1],
                 "order": 5,
                 }
            )
        else:
            pass

        if images:
            return images
        else:
            return None

    def update_(self, field, value):
        """
        The dataset is put in Edit() Mode. The list is updated and the field is forwarded to the helper
        which updates the field in büro+
        ! Important: Use the field names as used in Büro+
        :param field: string Ex 'ArtNr' on Artikel
        :param value: string the value for the field
        :return: dict self.fields_list
        """
        self.fields_list[field] = value

        if isinstance(value, datetime.datetime):
            value = value.strftime("%d.%m.%Y %H:%M:%S.%f")

        self.helper_set_value_of(field, value)

    def create_(self, field, value):
        self.fields_list[field] = value

        if isinstance(value, datetime.datetime):
            value = value.strftime("%d.%m.%Y %H:%M:%S.%f")

        self.helper_set_value_of(field, value)

    def copy_(self):
        """ Child classes need to take care of this """
        pass

    def edit_(self):
        """ To edit a give dataset """
        # self.start_transaction()
        self.created_dataset.Edit()

    def append_(self, *args, **kwargs):
        """ To create a Dataset """
        # self.start_transaction()
        self.created_dataset.Append(*args, **kwargs)

    def set_updated_fields(self, bridge_customer):

        self.created_dataset.SetSatzDatum(
            bridge_customer.created_at,
            self.get_("ErstBzr"),
            bridge_customer.updated_at,
            "GC-Auto"
        )

    def start_transaction(self):
        """ the table is locked until commit!"""
        self.created_dataset.StartTransaction()

    def post_(self):
        """ After making changes to the fields, post them into the dataset"""
        try:
            self.created_dataset.Post()
        except Exception as e:
            print(f"ERP Post gone wrong - Cancel | Error: {e}")
            self.cancel_()
            return e
        return True

    def cancel_(self):
        """
        If post or others fail, cancel must be called to revert the changes
        :return:
        """
        self.created_dataset.Cancel()

    """ ERP """

    def set_erp_obj(self, erp_obj):
        self.erp_obj = erp_obj

    def get_erp_obj(self):
        if self.erp_obj:
            return self.erp_obj
        else:
            return False

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
        return self.dataset

    def get_dataset_fields(self):
        return self.dataset_fields

    def set_created_dataset(self):
        """
        Get the content of the fields by calling CreateDataset(). All related tables are included
        :return:
        """
        self.created_dataset = self.get_dataset_infos().CreateDataSet()

    def get_created_dataset(self):
        return self.created_dataset

    def delete_dataset(self, check_delete=False):
        """ Delete with checks
        The delete without checks works fine
        """
        if check_delete:
            self.edit_()
            self.created_dataset.Delete()
            self.post_()

    def delete_dataset_with_check(self, gspkz="GspKz"):
        self.edit_()
        print(f"Is customer {self.get_('AdrNr')} locked?:", self.get_(gspkz))
        if self.get_(gspkz) == 1:
            self.update_(field=gspkz, value=0)
            self.post_()

        result = self.created_dataset.CheckDelete(aMeld=0, aIgnoreWarnings=0)
        result = True
        print("Result:", result)
        if result:
            self.delete_dataset(check_delete=result)
        else:
            self.edit_()
            self.update_(field=gspkz, value=1)
            self.post_()
        return result

    """ Positioning/Finding/Filtering """

    def set_dataset_cursor_to_field_value(self):
        found = self.created_dataset.FindKey(self.dataset_id_field, self.dataset_id_value)
        if not found:
            self.set_dataset_infos()  # <-----|
            #                                   |-- Creating the Dataset!!
            self.set_created_dataset()  # <-----|

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

        return self.created_dataset.FindKey(self.dataset_id_field, self.dataset_id_value)

    """ Range """
    def set_range(self, start, end=None, field=None):
        """
        Set a range by the give field with a list of indexes.
        !Important!
        When setting the range from (10026, 10030) only 10026-10029 is considered!!
        Example
        Adressen:
            set_range(start=10026, end=10027, field='Nr')
        Search for Adresses between 10026 and 10027 on the field NR

        Anschriften:
            set_range(start=([10026,0], end=[10027,10], field='AdrNrAnsNr'
        Search for Anschriften between Address 10026 and Anschrift 0 and
        Address 10027 and Anschrift 10

        :param start: list Could be a unique value: 10026 or a list [10026,1]
        :param end:  list Could be a unique value: 10026 or a list [10026,1]
        :param field: The index of the DataSet
        :return:
        """
        if field is None:
            field = self.dataset_id_field

        if end is None:
            end = start

        # Check if the start and end values are datetime objects
        if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
            # If yes, convert them to a string with microsecond precision
            start = str(start.strftime("%d.%m.%Y %H:%M:%S.%f"))
            end = str(end.strftime("%d.%m.%Y %H:%M:%S.%f"))
        else:
            # If not, check if they are lists and convert them if necessary
            if not isinstance(start, list):
                start = [start]
            if not isinstance(end, list):
                end = [end]

        # print("This is the range", field, start, end)
        self.created_dataset.SetRange(field, start, end)

        # Apply Range
        self.created_dataset.ApplyRange()
        # Check if we get results
        if self.range_count() == 0:
            print("\nNo", self.dataset_name, "in given range", start,"and", end)
            self.created_dataset.CancelRange()
            self.created_dataset = None

            return False
        # set the cursor to the first entry
        elif self.range_count() > 1:
            print("Found", self.range_count(), self.dataset_name, "between", start, end)
            self.range_first()
            return True
        elif self.range_count() == 1:
            print("Found 1 between", start, end)
            return True

    def set_range_wildcard(self, index_field, value):
        self.created_dataset.Indices(index_field).Select()
        self.created_dataset.WildcardRange(value)

    def range_next(self):
        self.created_dataset.Next()
        self.range_skip_gspkz()

    def range_first(self):
        self.created_dataset.First()
        self.range_skip_gspkz()

    def range_skip_gspkz(self):
        if self.skip_gspkz:
            while True:
                gspkz = self.get_("GspKz")
                if gspkz is not None and gspkz == 1 and not self.range_eof():
                    self.range_next()
                elif gspkz == 0:
                    break
        else:
            return True

    def range_eof(self):
        """
        Checks if the end of the table/range is reached and returns True.
        :return: Bool
        """
        return self.created_dataset.Eof

    def range_count(self):
        return self.created_dataset.RecordCount

    def is_ranged(self):
        return self.created_dataset.IsRanged()

    def is_empty(self):
        return self.created_dataset.IsEmpty

    def filter_and(self, filter_field, filter_value):
        self.created_dataset.Filter = f"{filter_field} = '{filter_value}'"
        # To add more filter, call self.filter_set
        # self.created_dataset.Filtered = True

    def filter_expression(self, expression):
        """
        !Wichtig Calc Fields können nicht gefiltert werden. Also in der Liste nachsehen ob das Feld mit einem * markiert ist. Die gehen nicht!

        Hier kann der Filterstring der Tabelle gesetzt werden. Damit können Datasets auch außerhalb der Funktionalität von Indices Datenmengen eingrenzen. Zum Löschen des Filters einfach einen leeren
        String übergeben. Wird ein Dataset gefiltert, können nur Datensätze gelesen werden, die dem Filter entsprechen. Hier ein Beispiel:
        Datenbankfeldname = 'gewünschter Filter Wert' OR Datenbankfeldname = 'anderer gewünschter
        Filter Wert' Falls der Filter auch leere Werte in der Ergebnismenge enthalten soll, verwenden Sie das
        Schlüsselwort "NULL".
        BelegNr <> 'RE000001' OR ArtNr = NULL
        Beispiel, wie ein Filter für Datumswerte aussieht:
        Delphi: 'Dat > ''30.03.2009''' Vb, c++ c#: „Dat > '30.03.2009'“
        Falls Feldnamen mit Leerzeichen verwendet werden, müssen diese in eckige Klammern gesetzt werden:
        [Meine Bezeichnung] = 'Filter Wert'

        < Linker Operator kleiner als der Rechte
        > Linker Operator größer als der Rechte
        >= Linker Operator größer oder gleich dem Rechten
        <= Linker Operator kleiner oder gleich dem Rechten
        = Linker und Rechter Operator gleich
        <> Linker und Rechter Operator sind ungleich
        AND Wahr, wenn Linker und rechter Ausdruck dasselbe Ergebnis liefern (Wahr oder Falsch
        Ausdruck)
        NOT Wahr wenn Linker und rechter Ausdruck ein unterschiedliches logisches Ergebnis liefern
        (Wahr oder Falsch Ausdruck)
        OR Entweder ist der Linke oder der Rechte Ausdruck wahr (Wahr oder falsch Ausdruck)

        :param expression:
        :return:
        """
        self.created_dataset.Filter = expression

    def filter_set(self):
        self.created_dataset.Filtered = True

    """ Helper """

    def helper_get_value_of(self, field, dataset=None):
        """
        Eval interprets a string as code.
        Example: We get AsString from field_types dict and add it to 'self.dataset.Fields.Item(str(field)).'
        Therefore we get 'self.dataset.Fields.Item(str(field)).AsString' which gives us the right field value
        Make sure all fields are in the dict
        :param field:
        :return:
        """

        if not dataset:
            dataset = self.get_created_dataset()

        field_type = dataset.Fields.Item(field).FieldType
        if field_type in self.field_types:
            # Remove the timezone from the date
            if field_type == "DateTime":
                is_date = eval('dataset.Fields.Item(str(field)).' + self.field_types[field_type])
                return is_date.replace(tzinfo=None)
            else:
                return eval('dataset.Fields.Item(str(field)).' + self.field_types[field_type])
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

        if field_type in self.field_types_to_set:
            print("Set %s as %s - %s" % (field, self.field_types_to_set[field_type], value))
            return exec('self.created_dataset.Fields("' +
                        str(field) +
                        '").' +
                        self.field_types_to_set[field_type] +
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
            with open(file, 'r') as f:
                print("Open file for prefill: ", self.prefill_json_directory + file)
                # data = json.load(f)
                try:
                    data = yaml.safe_load(f)
                    for key, value in data.items():
                        print("Creating fields for prefill:", key, value)
                        self.create_(key, value)
                except yaml.YAMLError as exc:
                    print(exc)

    def print_dataset_fields(self):
        for field in self.get_dataset_infos().Fields:
            print(field.Name)


