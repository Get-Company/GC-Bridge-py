# Child Model

from main.src.Controller.Bridge.BridgeObjectController import BridgeObjectController
# Entity for mapping and sync
from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *
from main.src.Controller.ERP.ERPController import *
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity
# Functions
import uuid
import re


class BridgeObjectProductController(BridgeObjectController):
    """
    :param dataset_lang: array An array of languages to translate to. Like ["de-DE", "en-EN"]
    """

    def __init__(self, dataset_lang=0):
        # Initiate all variables to forward them to super.__init__
        self.dataset = erp_get_dataset('Artikel')
        self.last_sync_date_field = "dataset_product_sync_date"
        self.dataset_field_ltzaend = "LtzAend"
        self.datetime_now = datetime.now()
        self.dataset_field_gspkz = "WShopKz"
        self.dataset_field_gspkz_must_be = True
        self.dataset_field_title = "KuBez1"
        self.dataset_field_img = "Bild"
        self.dataset_lang = dataset_lang
        self.img_file = 0  # JSON Object Like {"Bild1": "/some/path/to/image/image1.jpg", ...}
        self.amount_categories = 10  # Since we have 10 Slots in the product db of ERP
        self.dataset_field_categories = "ArtKat"  # Like ArtKat1, ArtKat2....
        self.class_name = "A-BOProdC"
        self.entity = BridgeProductEntity
        super().__init__(dataset=self.dataset,
                         last_sync_date_field=self.last_sync_date_field,
                         dataset_field_ltzaend=self.dataset_field_ltzaend,
                         dataset_field_gspkz=self.dataset_field_gspkz,
                         dataset_field_gspkz_must_be=self.dataset_field_gspkz_must_be,
                         dataset_field_title=self.dataset_field_title,
                         dataset_field_img=self.dataset_field_img,
                         class_name=self.class_name,
                         entity=self.entity,
                         dataset_lang=self.dataset_lang
                         )

    def dataset_save_to_db(self, dataset):
        self.print_method_info(self.class_name)
        #  2.1 Map dataset to entity
        entity = self.dataset_map_to_db(dataset)

        # 2.2 Upsert the entity to the db
        entity_inserted = self.dataset_upsert_entity(entity)
        print('Entity Inserted ID: "%s" ' % entity_inserted.id)

        # 3 Map dataset to entity language
        for language in self.dataset_get_languages():
            print('Loop for Languages - Current: "%s"' % language)
            # 1. Get the mapped entity for the language
            translation_entity = self.dataset_map_language_to_db(dataset, entity_inserted, language)
            # 2. Search for an already translated entry in the db and upsert
            self.dataset_upsert_language_entity(translation_entity, entity_inserted, language)

        # 4 Upsert the categories
        print('Entity Inserted for Categories: "%s" ' % entity_inserted.id)
        self.dataset_upsert_categories(dataset, entity_inserted)

        # 5 Upsert the tax
        print("Entity has tax?: %s" % entity_inserted.tax)
        self.dataset_upsert_tax(dataset, entity_inserted)

    def dataset_map_to_db(self, dataset):
        """
        This function calls the mapping which is setup in the corresponding Entity. All the field are mapped there
        :param dataset: object The entity
        :return:
        """
        self.print_method_info(self.class_name)
        print('Map "%s" to an entity ' % dataset.Fields.Item(self.dataset_field_title).AsString)

        # Get the image Call GE class
        self.img_file = self.dataset_get_image_filename(dataset)

        # Get mapped entity
        entity = map_product_erp_to_bridge_db(dataset, self.img_file)
        print("This is the entity", entity)

        return entity

    def dataset_upsert_entity(self, entity):
        self.print_method_info("A-BOProdC")
        # 1. Find actual entry in db by erp_nr
        entity_db = BridgeProductEntity.query.filter_by(erp_nr=entity.erp_nr).first()
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

    def dataset_map_language_to_db(self, dataset, entity, language):
        """
        This function calls the mapping which is set up in the corresponding Entity. All the field are mapped there
        :param dataset: object Dataset
        :param entity: object The Entity to which the translation belongs to
        :param language: string Like "de-DE"
        :return entity: object Entity of BridgeProductTranslationEntity
        """
        self.print_method_info("A-BOProdC")
        print('Map "%s" Language to an entity ' % dataset.Fields.Item(self.dataset_field_title).AsString)
        translation_entity = map_product_erp_language_to_bridge(dataset, entity, language)

        return translation_entity

    def dataset_upsert_language_entity(self, translation_entity, entity, language):
        """

        :param language: string Current ISO like "de-DE"
        :param translation_entity: object BridgeProductTranslationEntity
        :param entity: object BridgeProductEntity
        :return: 0
        """
        self.print_method_info("A-BOProdC")
        print('Set translation entity id: "%s"' % entity.id)
        translation_db = translation_entity.query. \
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

    def dataset_upsert_categories(self, dataset, product_entity):
        self.print_method_info("A-BOProdC")
        print('Upsert "%s" categories for Product "%s"' % (self.amount_categories, product_entity.name))
        category_entity = BridgeCategoryEntity

        # Loop through the categories from the product
        for c in range(1, self.amount_categories + 1):
            # Get the category id from the dataset
            dataset_cat_id = dataset.Fields.Item(self.dataset_field_categories + str(c)).AsInteger
            category_entity_db = category_entity.query.filter_by(erp_nr=dataset_cat_id).first()
            # If we got a category id
            if dataset_cat_id and category_entity_db:
                print('Category id in Product dataset: "%s"' % dataset_cat_id)
                # Get the category entity from db for current product
                print('Category Nr "%s" found in DB - Name:"%s"' % (dataset_cat_id, category_entity_db.title))
                # Check if we already have this in bridge_product_category_entity
                prod_cat_found = product_entity.check_if_prod_cat(category_entity_db.id, product_entity.id)
                if prod_cat_found:
                    print('Relation between Category "%s" and Product "%s" is already in DB. Skip this one' % (
                        category_entity_db.id, product_entity.id
                    )
                          )
                    return
                else:

                    print('Product: %s' % product_entity.name)
                    print('Category: %s' % category_entity_db.title)
                    product_entity_new = product_entity.categories.append(category_entity_db)
                    print("Product Entity New:")
                    print(product_entity_new)
                    db.session.commit()
            else:
                return

    def dataset_upsert_tax(self, dataset, product_entity):
        self.print_method_info("A-BOProdC")
        print('Upsert "%s" Tax for Product "%s"' % (self.amount_categories, product_entity.name))
        tax_entity = BridgeTaxEntity

        dataset_tax_steuer_schluessel = dataset.Fields.Item("StSchl").AsString
        # The string we get is like: 20 Mehrwertsteuer 29%. we just need the first Digit -> 20
        pattern = "(\d{1,})"
        print("Suche nach Steuerschlüssel in %s" % dataset_tax_steuer_schluessel)
        match = re.search(pattern, dataset_tax_steuer_schluessel)

        tax_entity_db = tax_entity.query.filter_by(steuer_schluessel=match.group(1)).first()
        print("Tax found: %s" % tax_entity_db.description)

        product_entity.tax = tax_entity_db
        print("Tax relation to product: %s" % product_entity.tax.description)

        db.session.commit()

    def dataset_upsert_price(self, dataset, product_entity, language):
        pass

    def dataset_get_image_filename(self, dataset):
        self.print_method_info(self.class_name)
        """
        Simply return the image filename from a path string
        :return: json Image filename
        """
        # Get the images
        print('Search for Image in Field: "%s" ' % self.dataset_field_img)
        img1_path = dataset.Fields.Item(self.dataset_field_img).GetEditObject(4).LinkFileName
        img1 = self.find_image_filename_in_path(img1_path)

        img2_path = dataset.Fields.Item(self.dataset_field_img + "2").GetEditObject(4).LinkFileName
        img2 = self.find_image_filename_in_path(img2_path)

        img3_path = dataset.Fields.Item(self.dataset_field_img + "3").GetEditObject(4).LinkFileName
        img3 = self.find_image_filename_in_path(img3_path)

        img4_path = dataset.Fields.Item(self.dataset_field_img + "4").GetEditObject(4).LinkFileName
        img4 = self.find_image_filename_in_path(img4_path)

        img5_path = dataset.Fields.Item(self.dataset_field_img + "5").GetEditObject(4).LinkFileName
        img5 = self.find_image_filename_in_path(img5_path)

        # Make a JSON Object
        images_json = {
            "Bild1": img1,
            "Bild2": img2,
            "Bild3": img3,
            "Bild4": img4,
            "Bild5": img5,
        }
        print("Images JSON Object", images_json)

        return images_json

    def dataset_get_by_artikel_number(self, artikel_number="204013"):
        dataset = self.dataset
        erp_get_dataset_by_id(dataset, "Nr", artikel_number)
        return dataset
