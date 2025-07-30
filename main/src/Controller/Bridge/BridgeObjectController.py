# Models
from sqlalchemy.orm import joinedload

from main.src.Controller.ERP.ERPController import *
# Functions
from datetime import datetime
import os
import re
from main import db
# To get the method names
import inspect
# For the image json object
import json
from loguru import logger


from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from main.src.Repository.functions_repository import write_log


class BridgeObjectController:
    """
    ERP -> DB
    -----------
    1. BOC dataset_save_changed_to_db()
    2. BOC dataset_get_changed_by_range()
    3. BOC dataset_save_to_db()
    4. Child dataset_map_to_db()
    5. BOC dataset_get_image_filename()
    6. BOC dataset_set_languages()
    7. Child dataset_upsert_entity()
    8. Child dataset_set_sync_date()
    9. Child dataset_get_sync_date()
    
    """

    def __init__(self,
                 dataset,
                 last_sync_date_field,
                 dataset_field_ltzaend,
                 dataset_field_gspkz,
                 dataset_field_gspkz_must_be,
                 dataset_field_title,
                 dataset_field_img,
                 class_name,
                 entity,
                 dataset_lang=0
                 ):
        """
        :param dataset: object Dataset
        :param last_sync_date: object BridgeSynchronizeEntity.*the field for this name*
        :param dataset_field_ltzaend: string Like "LtzAend" The field that holds the last sync date in the dataset
        :param dataset_field_gspkz: string Like "GspKz" The field if the dataset is active
        :param dataset_field_title: string Like "KuBez1" or "Bez" The field that holds the title for the info print
        :param dataset_field_img: string Like "Bild" The field that holds the img
        :param dataset_lang: array An array of languages to translate to. Like ["de-DE", "en-EN"]
        """
        self.dataset = dataset
        self.last_sync_date = self.dataset_get_sync_date()
        self.last_sync_date_field = last_sync_date_field
        self.dataset_field_ltzaend = dataset_field_ltzaend
        self.dataset_field_gspkz = dataset_field_gspkz
        self.dataset_field_gspkz_must_be = dataset_field_gspkz_must_be
        self.dataset_field_title = dataset_field_title
        self.dataset_field_img = dataset_field_img
        self.entity = entity
        self.class_name = class_name

        if not dataset_lang:
            self.dataset_lang = ["de-DE", "en-EN"]
        else:
            self.dataset_lang = dataset_lang

        self.img_file = 0

    def print_method_info(self, name):
        logger.info('\n#- %s %s -#' % (name, inspect.currentframe().f_back.f_code.co_name))
        write_log('#- %s %s -#' % (name, inspect.currentframe().f_back.f_code.co_name))

    def dataset_save_changed_to_db(self):
        """
        This is heritated to the child classes. Simply call it from a Child.
        :return:
        """
        self.print_method_info(self.class_name)
        # Get changed datasets by date
        dataset_changed = self.dataset_get_changed_by_range()
        # 2. Loop
        if dataset_changed and erp_get_dataset_record_count(dataset_changed) >= 1:
            logger.info('Match! Enter the Loop for : "%s"'
                  % dataset_changed.Fields.Item(self.dataset_field_title).AsString)

            i = 0
            # Call the erp function for the amount of records
            logger.info("%s Record(s) found" % erp_get_dataset_record_count(dataset_changed))
            while i < erp_get_dataset_record_count(dataset_changed):
                logger.info('In Loop nr: %s' % i)
                logger.info('Check for "%s". "%s" = "%s"' % (
                    self.dataset_field_gspkz,
                    dataset_changed.Fields.Item(self.dataset_field_gspkz).AsBoolean,
                    self.dataset_field_gspkz_must_be))
                # Check if active (field is 0/False)
                if dataset_changed.Fields.Item(self.dataset_field_gspkz).AsBoolean == self.dataset_field_gspkz_must_be:
                    logger.info('Is active, last sync (%s) and needs sync: "%s"' %
                          (
                              self.dataset_field_ltzaend,
                              dataset_changed.Fields.Item(self.dataset_field_title).AsString
                          ))
                    # 2.1 Map and
                    # 2.2 Upsert
                    self.dataset_save_to_db(dataset_changed)

                dataset_changed.Next()

                # Add 1 to the iterator
                i += 1

        else:  # dataset_changed
            logger.info("... nothing found - no changes. Exit.")
            return False

        self.dataset_set_sync_date()

    def dataset_save_all_to_db(self):
        self.print_method_info(self.class_name)

        i = 0
        # Call the erp function for the amount of records
        logger.info('We have got %s Entries to save! Lets go.' % erp_get_dataset_record_count(self.dataset))
        while i < erp_get_dataset_record_count(self.dataset):
            # Check if active (field is 0/False
            logger.info("%s should be %s. Is->%s" % (
                self.dataset_field_gspkz,
                self.dataset_field_gspkz_must_be,
                self.dataset.Fields.Item(self.dataset_field_gspkz).AsBoolean))
            if self.dataset.Fields.Item(self.dataset_field_gspkz).AsBoolean == self.dataset_field_gspkz_must_be:
                logger.info('Is active and needs sync: "%s"' %
                      self.dataset.Fields.Item(self.dataset_field_title).AsString)
                # 2.1 Map and
                # 2.2 Upsert
                self.dataset_save_to_db(self.dataset)

            self.dataset.Next()

            # Add 1 to the iterator
            i += 1

        self.dataset_set_sync_date()

    def dataset_get_changed_by_range(self):
        self.print_method_info(self.class_name)

        """
        Overwrite this method for more ranges or different ranges
        :return:
        """
        # Set range
        dataset_changed = erp_set_dataset_range_by_date(
            self.dataset,
            self.dataset_field_ltzaend,
            self.last_sync_date,
            datetime.now()
        )
        if dataset_changed:
            # Apply range
            dataset_changed = erp_apply_dataset_range(dataset_changed)
            return dataset_changed
        else:
            return False

    def dataset_save_to_db(self, dataset):
        pass

    def dataset_map_to_db(self, dataset):
        logger.info("\n#- BOC dataset_map_to_db -#")
        """
        This function is called in the child. The mapping depends on which Entity is mapped.
        So the right Entity is imported in the child and the mapping happens there.
        :param dataset: object Dataset
        :return: object The Entity
        """
        pass

    def dataset_map_language_to_db(self, dataset, entity, language):
        logger.info("\n#- BOC dataset_map_to_db -#")
        """
        This function is called in the child. The mapping depends on which Entity is mapped.
        So the right Entity is imported in the child and the mapping happens there.
        :param dataset: object Dataset
        :param entity: object The entity to which the language should be mapped to
        :return: object The Entity
        """
        pass

    def dataset_get_image_filename(self, dataset):
        pass

    def dataset_get_languages(self):
        self.print_method_info(self.class_name)
        """
        Set the languages by an array like lang = ["de-DE", "en-EN"]
        If nothing is set, use de-DE and en-EN
        :param: self.dataset_lang array
        :return: array of languages iso
        """
        if self.dataset_lang:
            logger.info("Languages are given: ", self.dataset_lang)
            return self.dataset_lang
        else:
            logger.info('"No Language is given. Fallback to "de-DE" and "en-EN"')
            return ["de-DE", "en-EN"]

    def dataset_upsert_entity(self):
        self.print_method_info(self.class_name)
        """
        This function is called in the child. We have to deal with special fields and cases, so its better to
        individualize the upsert process.
        :return:
        """
        pass

    def dataset_upsert_language_entity(self, translation, entity, language):
        self.print_method_info(self.class_name)
        """
        This function is called in the child. We have to deal with special fields and cases, so its better to
        individualize the upsert process.
        :return:
        """
        pass

    def dataset_set_sync_date(self):
        self.print_method_info(self.class_name)
        bridge_synchronize_entity = BridgeSynchronizeEntity().get_entity_by_id_1()
        setattr(bridge_synchronize_entity, self.last_sync_date_field, datetime.now())
        db.session.add(bridge_synchronize_entity)
        db.session.commit()
        return datetime.now()

    def dataset_get_sync_date(self):
        """
        Get the date from db regarding the Entity defined by self.last_sync_date_field
        Returns the datetime as object
        :return: object datetime.datetime
        """
        self.print_method_info("A-BOC")
        bridge_synchronize_entity = BridgeSynchronizeEntity()
        current_dates = bridge_synchronize_entity.get_entity_by_id_1()
        logger.info('Get last sync date from field: %s' % self.last_sync_date_field)
        last_sync_date = getattr(current_dates, self.last_sync_date_field)
        if last_sync_date:
            logger.info('Last sync date: "%s"' % last_sync_date.strftime("%d.%m.%Y %H:%M:%S"))
            return last_sync_date
        else:
            self.dataset_set_sync_date()
            return datetime.now()

    def find_image_filename_in_path(self, image_link_or_path):
        img_link = image_link_or_path
        if img_link:
            # Cuts the whole path leaves the image. Like "900000.jpg"
            pattern = "[\w-]+.(jpg|jpeg|png|gif|webp)"
            m = re.search(pattern, img_link)
            if m:
                img = m.group(0)
                logger.info('Image Link found: "%s"' % img)
            else:
                img = 0
                logger.info('Could not find img in Path: "%s"' % img_link)
        else:
            img = 0
            logger.info("No Image in erp? Nothing found!")

        return img

