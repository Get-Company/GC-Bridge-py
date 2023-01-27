from main.src.Entity.ERP.NestedDataSets.ERPNestedDatasetObjectEntity import ERPNestedDatasetObjectEntity

"""
Attention: NestedDataSet
Currency is the NestedDataSet from Mandant and its called FrW (yes USt)
We have to set the NestedDataSet as the Created Dataset in this class to get all the functions
Have a look at"""


class ERPCurrencyEntity(ERPNestedDatasetObjectEntity):

    def __init__(self, erp_obj, nested_dataset_id_value=None, nested_dataset_range=None):
        self.erp_obj = erp_obj

        """ Parent """
        self.dataset_name = 'Mandant'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = 58
        self.dataset_range = None

        """ Nested """
        self.nested_dataset_name = 'FrW'
        self.nested_dataset_id_field = 'ISOBez'  # ISO3 EUR, CHF usw
        self.nested_dataset_id_value = nested_dataset_id_value
        self.nested_dataset_range = nested_dataset_range
        self.prefill_json_directory = None

        """ Functions before the super INIT"""
        self.set_is_nested(True)

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

    def get_iso3(self, iso3):
        self.set_nested_range(start=iso3, end=iso3)
        self.range_first()
        print(self.get_("BaWFak"))
        return self

    def set_currency(self, bridge_entity):
        """
        Todo: Does not work properly. It cannot find ISOBez CHF in ERP? Why

        :param bridge_entity:
        :return:
        """
        self.created_dataset.Edit()
        nested_created_dataset = self.created_dataset.NestedDatasets[self.nested_dataset_name]

        nested_created_dataset.SetRangeStart()
        nested_created_dataset.Fields["ISOBez"].AsString = "CHF"
        nested_created_dataset.Fields["KuBez"].AsString = "SFr"
        nested_created_dataset.SetRangeEnd()
        nested_created_dataset.Fields["ISOBez"].AsString = "CHF"
        nested_created_dataset.Fields["KuBez"].AsString = "SFr"
        nested_created_dataset.ApplyRange()
        nested_created_dataset.First()
        print(nested_created_dataset.Fields["ISOBez"].AsString)
        nested_created_dataset.Edit()
        nested_created_dataset.Fields['BaWFak'].AsFloat = bridge_entity.rate
        nested_created_dataset.Post()
        nested_created_dataset.PostNestedDataset()

        self.created_dataset.Post()





    """
    List of fields
    24.01.2023
    
    ###
    
    NestedDataSet: FrW - Fremdwährungen
        Field: KuBez - Kurzbezeichnung (UnicodeString) +
        Field: Land - Land (Integer) +
        Field: Bez - Bezeichnung (UnicodeString) +
        Field: ISOBez - ISO Bezeichnung (UnicodeString) +
        Field: FrWFak - Fremdwährungsfaktor (Double) +
        Field: BaWFak - Basiswährungsfaktor (Double) +
        Field: Flags - Flags (Integer) /
        Field: *PStartKz - Bei Programmstart abfragen (Boolean) +
        Field: *BasisWKz - Ist Basiswährung (Boolean) +
        Field: *LW1Kz - Ist Leitwährung 1 (Boolean) +
        Field: *LW2Kz - Ist Leitwährung 2 (Boolean) +
        Field: *FestKursKz - Hat festen Wechselkurs (Boolean) +
        Field: LtzDat - Letzte Änderung (DateTime) +
        Field: Info - Information (Info) +
        Field: *InfoKz - Information Kennzeichen (Boolean) +
        Field: *Kurs - Kurs (UnicodeString) +
        Field: SatzDat - Satzdatum (Array) /
        Field: *ErstDat - Erstellungsdatum (DateTime) +
        Field: *ErstBzr - Benutzer bei Erstellung (String) +
        Field: *AendDat - Änderungsdatum (DateTime) +
        Field: *AendBzr - Benutzer bei Änderung (String) +
        Index: ISOBez - ISO-Bezeichnung
          IndexField:ISOBez - ISO Bezeichnung
        Index: KuBez - Kurzbezeichnung
          IndexField:KuBez - Kurzbezeichnung
    """

