# Child Model

from main.src.Controller.Bridge.BridgeObjectController import BridgeObjectController
# Entity for mapping and sync
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *
from main.src.Controller.ERP.ERPController import *
from main.src.Repository.functions_repository import write_log
# Functions
import uuid


class BridgeObjectCategoryController(BridgeObjectController):
    """
    :param dataset_lang: array An array of languages to translate to. Like ["de-DE", "en-EN"]
    """

    def __init__(self, dataset_lang=0):
        # Initiate all variables to forward them to super.__init__
        self.dataset = erp_get_dataset('ArtikelKategorien')
        self.last_sync_date_field = 'dataset_category_sync_date'
        self.dataset_field_ltzaend = "LtzAend"
        self.datetime_now = datetime.now()
        self.dataset_field_gspkz = "GspKz"
        self.dataset_field_gspkz_must_be = False
        self.dataset_field_title = "Bez"
        self.dataset_field_img = "Bild"
        self.dataset_lang = dataset_lang
        self.img_file = 0
        self.class_name = "A-BOCatC"

        super().__init__(self.dataset,
                         self.last_sync_date_field,
                         self.dataset_field_ltzaend,
                         self.dataset_field_gspkz,
                         self.dataset_field_gspkz_must_be,
                         self.dataset_field_title,
                         self.dataset_field_img,
                         self.class_name,
                         self.dataset_lang
                         )

    def dataset_save_to_db(self, dataset):
        self.print_method_info(self.class_name)
        #  2.1 Map dataset to entity
        entity = self.dataset_map_to_db(dataset)

        # 2.2 Upsert the entity to the db
        entity_inserted = self.dataset_upsert_entity(entity)
        print('Entity Inserted ID: "%s" ' % entity_inserted.id)
        write_log('%s Inserted' % entity_inserted.title)

    def dataset_map_to_db(self, dataset):
        """
        This function calls the mapping which is setup in the corresponding Entity. All the field are mapped there
        :param dataset: object The entity
        :return:
        """
        self.print_method_info(self.class_name)
        print('Map "%s" to an entity ' % dataset.Fields.Item(self.dataset_field_title).AsString)
        write_log('Map "%s" to an entity ' % dataset.Fields.Item(self.dataset_field_title).AsString)
        # Get the image Call GE class
        self.img_file = self.dataset_get_image_filename(dataset)

        # Get mapped entity
        entity = map_category_erp_to_bridge_db(dataset, self.img_file, self.dataset_lang)
        print("This is the entity", entity)

        return entity

    def dataset_upsert_entity(self, entity):
        self.print_method_info("A-BOCatC")
        # 1. Find actual entry in db by erp_nr
        print("Find ERP_NR: %s" % entity.erp_nr)
        entity_db = BridgeCategoryEntity.query.filter_by(erp_nr=entity.erp_nr).first()
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

    def dataset_upsert_language_entity(self, translation_entity, entity, language):
        """

        :param language: string Current ISO like "de-DE"
        :param translation_entity: object BridgeProductTranslationEntity
        :param entity: object BridgeProductEntity
        :return: 0
        """
        self.print_method_info("A-BOCatC")
        print('Set translation entity id: "%s"' % entity.id)
        translation_db = translation_entity.query.\
            filter_by(language_iso=language). \
            filter_by(product_id=entity.id). \
            first()

        if translation_db:
            print('Update translation from "%s" to "%s"' % (translation_db.name, entity.name))
            translation_db.update_entity(translation_entity)
            db.session.add(translation_db)
        else:
            print('Add translation "%s"' % translation_entity.name)
            translation_entity.product = entity
            db.session.add(translation_entity)

        db.session.commit()

    def dataset_get_image_filename(self, dataset):
        """
        Simply return the image filename from a path string
        :return: string Image filename
        """
        # Get the images
        print('Search for Image in Field: "%s" ' % self.dataset_field_img)
        img_path = dataset.Fields.Item(self.dataset_field_img).GetEditObject(4).LinkFileName
        img = self.find_image_filename_in_path(img_path)

        return img
