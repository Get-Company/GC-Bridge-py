from main.src.Controller.ControllerObject import ControllerObject
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from sqlalchemy import inspect

from loguru import logger

from main import db
import uuid
from datetime import datetime


class Bridge2ObjectController(ControllerObject):
    def __init__(self,
                 erp_obj,
                 erp_entity,
                 erp_entity_index_field,
                 bridge_entity,
                 bridge_entity_index_field,
                 entity_name,
                 filter_expression=None,

                 ):

        self.erp_obj = erp_obj
        self.bridge_synchronize_entity = BridgeSynchronizeEntity().get_entity_by_id_1()

        # Is it Categories or Products or Customers?
        self.erp_entity = erp_entity
        self.erp_entity_index_field = erp_entity_index_field  # The id field in ERP ex. Artikel = 'ArtNr'
        self.bridge_entity = bridge_entity
        self.bridge_entity_index_field = bridge_entity_index_field  # The id field in DB ex. Product = 'erp_nr'

        self.db = db
        self.uuid = uuid
        self.entity_name = entity_name

        self.filter_expression = filter_expression

        self.logger = logger

        super().__int__(erp_obj)

    def apply_filter(self):
        """
        A filter must be set in example Product/Artikel. We set the filter to WShopKz = True
        :return:
        """
        if self.filter_expression:
            print("Filter is set:", self.filter_expression)
            self.erp_entity.filter_expression(self.filter_expression)
            self.erp_entity.filter_set()
        else:
            print("No Filter is set")
            pass

    def set_bridge_entity(self):
        """
        Necessary for each child, since the sync loop needs to set the entity on each run
        :return:
        """
        pass

    def set_sync_all_range(self):
        """
        Needs to be called in the child. It sets the range for all records, depending on the
        index field and the index values...
        :return:
        """
        pass

    def set_sync_last_changed_range(self):
        """
        Needs to be called in the child. It sets the range for all changed records, depending on the
        index field and the bridge entity last changed date...
        :return: Bool
        """
        pass

    def sync_all(self):
        self.set_sync_all_range()
        # Filter the results
        self.apply_filter()
        self.upsert()
        return True

    def sync_changed(self):
        is_ranged = self.set_sync_last_changed_range()
        if is_ranged:
            # Filter the results
            self.apply_filter()
            self.upsert()
            return True

    def sync_one(self, value):
        self.erp_entity.set_range(start=value)
        self.apply_filter()
        self.upsert()
        return True

    def sync_range(self, start, end, field=None):
        """
        !Important!
        When setting the range from (10026, 10030) only 10026-10029 is considered!!
        :param start: value, int, str
        :param end: value, int, str !! The last one is not considered!
        :param field:
        :return:
        """
        self.erp_entity.set_range(start=start, end=end, field=field)
        self.apply_filter()
        self.upsert()
        return True

    def upsert(self):

        """
        Checks if the erp_entity is already in the db -> Update or not -> Insert
        :return:
        """
        self.erp_entity.range_first()
        # print(self.erp_entity.is_ranged(), self.erp_entity.range_eof())
        i = 0
        while not self.erp_entity.range_eof():

            self.before_upsert(current_erp_entity=self.erp_entity)

            # Always get a new instance of Bridge_Entity
            self.set_bridge_entity()

            entity_mapped_to_db = self.bridge_entity.map_erp_to_db(self.erp_entity)
            entity_in_db = self.is_in_db()

            # Is in DB - Update
            if entity_in_db:
                # logger.add("Update: ", entity_in_db)
                print("Update", entity_in_db)
                entity_in_db.update_entity(entity_mapped_to_db)
                entity_to_insert = self.reset_relations(entity_in_db)

            # Is not in DB - Insert
            elif entity_in_db is None:
                print("Insert", entity_mapped_to_db)
                entity_to_insert = entity_mapped_to_db

            else:
                return False
            self.db.session.add(entity_to_insert)

            if i >= 50:
                print(f"Commit Session - Buffer full: {i}")
                self.commit_session()
                i = 0
                print(f"Reset Buffer Counter to {i}=0")
            else:
                print(f"Fill Session Buffer {i}/50")

            i = i+1
            self.erp_entity.range_next()

        # Here we set the attribute/field of dataset_NAME_sync_date by the entity_name
        # We need to set it BEFORE the sync. So we can query the db for the last sync session
        # by range last_sync - now()
        setattr(self.bridge_synchronize_entity, 'dataset_' + self.entity_name + '_sync_date', datetime.now())
        self.db.session.add(self.bridge_synchronize_entity)

        # Commit everything
        self.commit_session()

    def is_in_db(self):
        """
        Check if the entity is in db. Use the standard ERP id field = 'ArtNr' and standard DB id field = erp_nr for Artikel
        The code example would look like:
        self.bridge_entity.query.filter_by(erp_nr=104014).first()
        erp=104014:
            bridge_entity_index_field = self.erp_entity.get_(self.erp_entity_index_field))
        :return: object
        """
        print("Parent is_in_db")
        bridge_entity_index_field = self.bridge_entity_index_field
        if bridge_entity_index_field:
            in_db = eval(
                'self.bridge_entity.query.filter_by(' + self.bridge_entity_index_field + '=self.erp_entity.get_(self.erp_entity_index_field)).first()')
            return in_db
        else:
            return None

    def reset_relations(self, bridge_entity):
        """
        After the entity was either updated&mapped (in db) or just mapped (new) all the relations must be set.
        This is done in the child, depending on the relations
        :param bridge_entity:
        :return: BridgeEntity updated
        """
        return bridge_entity

    def get_erp_entity(self):
        if self.erp_entity:
            return self.erp_entity

    def upsert_relations(self, entity):
        """
        Until now, this is only needed for the customer_address, addresses and contacts.
        The .upsert function does a while loop. All relations should be upserted before .upsert.
        :return:
        """
        pass

    def commit_session(self):
        try:
            self.db.session.commit()
        except:
            print("Error Commit Session")

    def before_upsert(self, current_erp_entity):
        pass

