import string

import win32com.client as win32
import pythoncom
import logging

# Get ERP
pythoncom.CoInitialize()
erp = win32.dynamic.Dispatch('BpNT.Application')



# erp = win32.gencache.EnsureDispatch('BpNT.Application')
# erp = win32.Dispatch('BpNT.Application')

def erp_test(mandant="Test"):
    print(erp.Init('Egon Heimann GmbH', "", 'f.buchner', ''))


def erp_connect(mandant="TEST"):
    # Connect ERP
    erp.Init('Egon Heimann GmbH', "", 'f.buchner', '')
    erp.SelectMand(mandant)
    print('ERP Connection Mandant "%s" hergestellt: ' % mandant, erp)
    return erp


def erp_get_dataset(name):
    dataset = erp_get_dataset_infos(name)
    return dataset.CreateDataSet()


def erp_get_dataset_infos(name):
    dataset_info = erp.DataSetInfos.Item(name)
    return dataset_info


def erp_close():
    # Absolute necessary step
    # erp.LogOff()
    erp.DeInit()
    print("ERP Connection geschlossen: ", erp)


def erp_get_dataset_record_count(dataset):
    """
    Simply return the number of elements in the give dataset
    :param dataset:
    :return The sum of the elements in the give dataset:
    """
    if dataset.RecordCount:
        return dataset.RecordCount
    else:
        return False


def erp_set_dataset_range_by_date(dataset, field, start, end):
    """
    Set the range by date
    !IMPORTANT! Range is not applied!
    !IMPORTANT! Earliest Date first
    :param dataset: Dataset
    :param field: string
    :param start: datetime
    :param end: datetime
    :return Dataset with applied range:
    """
    # Format the dates
    start_format = start.strftime("%d.%m.%Y %H:%M:%S")
    end_format = end.strftime("%d.%m.%Y %H:%M:%S")
    print('Range from: "%s" - to: "%s" in Field: "%s"' %
          (
              start,
              end,
              field
          )
          )
    # Stringify the values
    field_string = str(field)
    start_string = str(start_format)
    end_string = str(end_format)

    # Call the range function
    ranged_dataset = erp_set_dataset_range(dataset, field_string, start_string, end_string)

    # Return the range if it exists
    if ranged_dataset.isRanged():
        return ranged_dataset
    else:
        return False


def erp_set_dataset_range(dataset, field, start, end):
    """
    Set the range and return the dataset.
    !IMPORTANT! Range is not applied!
    You can set as many ranges you want and apply it in the last step
    :param dataset: object Dataset
    :param field: string The field for the range
    :param start: string
    :param end: string
    :return: Dataset with range set
    """
    # Set the range
    dataset.SetRange(field, start, end)

    return dataset


def erp_apply_dataset_range(dataset):
    """
    Applies the Range(s) that have been set before and sets the cursor to the first Item
    :param dataset: object Dataset
    :return: Dataset with applied ranges
    """
    # Apply the Range
    dataset.ApplyRange()
    # Set cursor on the first element of the range
    dataset.First()

    return dataset


def erp_get_dataset_by_id(dataset, field, id_value):
    """
    Sets the cursor on the record matching field and its id
    Example:(dataset.FindKey('Nr', '210')
    'Nr' would be field
    '210' would be id_value
    Return only dataset, since dataset_found is just a bool
    :param dataset: object Dataset
    :param field: string
    :param id_value: string
    :return: Dataset with the cursor on the record
    """
    dataset_found = dataset.FindKey(field, id_value)
    if dataset_found:
        return dataset
    else:
        return False


def erp_print_index_fields(dataset_name: str) -> None:
    """
    Simply prints all Indices names and Fieldinfos
    Example:
    Index: MFS - Mehrfachsuche
    Index: ID - ID
        IndexField:ID - ID
    Index: Nr - Nummer
        IndexField:AdrNr - Adressnummer
    aso...
    :param dataset_name: string Like "Adressen" or "Anschriften"
    :return: None
    """
    da = erp_get_dataset_infos(dataset_name)
    for Index in da.Indices:
        print("Index: %s" % Index.Name)
        for IndexField in Index.IndexFields:
            print("  %s: %s" % (IndexField.Name, IndexField.Info))
