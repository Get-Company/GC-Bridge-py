# Child Model

from main.src.Controller.Bridge.BridgeObjectController import BridgeObjectController
from main.src.Controller.ERP.ERPController import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import *
# Functions
import uuid


class BridgeObjectTaxController(BridgeObjectController):
    """
    :param dataset_lang: array An array of languages to translate to. Like ["de-DE", "en-EN"]
    """

    def __init__(self, dataset_lang=0):
        # Initiate all variables to forward them to super.__init__

        # We need to ask the mandant for the different taxes. They are NestedDataSets:
        self.parent_dataset = erp_get_dataset('Mandant')
        self.dataset = self.parent_dataset.NestedDataSets("Ust")

        self.last_sync_date_field = "dataset_tax_sync_date"
        self.dataset_field_ltzaend = "AendDat"
        self.datetime_now = datetime.now()
        self.dataset_field_gspkz = "StSchl"
        self.dataset_field_gspkz_must_be = True
        self.dataset_field_title = "Bez"
        self.dataset_field_img = "Bild"
        self.dataset_lang = dataset_lang
        self.img_file = 0  # JSON Object Like {"Bild1": "/some/path/to/image/image1.jpg", ...}
        self.amount_categories = 10  # Since we have 10 Slots in the product db of ERP
        self.dataset_field_categories = "ArtKat"  # Like ArtKat1, ArtKat2....
        self.class_name = "A-BOTaxC"
        self.entity = BridgeTaxEntity()
        super().__init__(self.dataset,
                         self.last_sync_date_field,
                         self.dataset_field_ltzaend,
                         self.dataset_field_gspkz,
                         self.dataset_field_gspkz_must_be,
                         self.dataset_field_title,
                         self.dataset_field_img,
                         self.class_name,
                         self.dataset_lang)

    def dataset_save_all_to_db(self):
        self.print_method_info(self.class_name)

        i = 0
        # Call the erp function for the amount of records
        print('We have got %s Entries to save! Lets go.' % erp_get_dataset_record_count(self.dataset))
        while i < erp_get_dataset_record_count(self.dataset):

            self.dataset_save_to_db(self.dataset)

            self.dataset.Next()

            # Add 1 to the iterator
            i += 1

        self.dataset_set_sync_date()

    def dataset_save_to_db(self, dataset):
        self.print_method_info(self.class_name)
        #  1.1 Map dataset to entity
        entity = self.dataset_map_to_db(dataset)

        # 1.2 Upsert the entity to the db
        entity_inserted = self.dataset_upsert_entity(entity)
        print('Entity Inserted ID: "%s" ' % entity_inserted.id)

    def dataset_map_to_db(self, dataset):
        """
        This function calls the mapping which is setup in the corresponding Entity. All the field are mapped there
        :param dataset: object The entity
        :return:
        """
        self.print_method_info(self.class_name)
        print('Map "%s" to an entity ' % dataset.Fields.Item(self.dataset_field_title).AsString)

        # Get mapped entity
        entity = map_tax_erp_to_bridge_db(dataset)
        print("This is the entity", entity)

        return entity

    def dataset_upsert_entity(self, entity):
        self.print_method_info(self.class_name)
        print(f"Tax Entity ID: {entity.id}")
        # 1. Find actual entry in db by erp_nr
        entity_db = BridgeTaxEntity.query.filter_by(steuer_schluessel=entity.steuer_schluessel).first()
        # Found one?
        if entity_db:
            print("Found in db. Updating.")
            entity_db.update_entity(entity)
            # Prepare update
            db.session.add(entity_db)
            # For following use
            entity_to_insert = entity_db
        # If there is no erp_nr in db, create it
        else:
            print('Not in db. Creating.')
            # Set the changeable fields
            entity_to_insert = entity
            entity_to_insert.api_id = uuid.uuid4().hex
            # Prepare create
            db.session.add(entity_to_insert)

        db.session.commit()

        # self.dataset_set_sync_date(entity)
        return entity_to_insert
