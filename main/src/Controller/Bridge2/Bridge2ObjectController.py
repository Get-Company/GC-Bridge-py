from main.src.Controller.ControllerObject import ControllerObject
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity

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
                 filter_expression=None
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

        super().__int__(erp_obj)

    def apply_filter(self):
        """
        A filter must be set in example Product/Artikel. We set the filter to WShopKz = True
        :return:
        """
        if self.filter_expression:
            self.erp_entity.filter_expression(self.filter_expression)
            self.erp_entity.filter_set()
        else:
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
        self.erp_entity.set_range(value, value)
        self.apply_filter()
        self.upsert()
        return True
    
    def sync_range(self, start, end):
        self.erp_entity.set_range(start, end)
        self.apply_filter()
        self.upsert()
        return True

    def upsert(self):
        """
        Checks if the erp_entity is already in the db -> Update or not -> Insert
        :return:
        """
        self.erp_entity.range_first()
        while not self.erp_entity.range_eof():
            print("Upsert %s: %s" % (self.entity_name, self.erp_entity.get_(self.erp_entity_index_field)))
            # Always get a new instance of Bridge_Entity
            self.set_bridge_entity()
            entity_mapped_to_db = self.bridge_entity.map_erp_to_db(self.erp_entity)
            entity_in_db = self.is_in_db()
            # Is in DB - Update
            if entity_in_db:
                print("Update")
                entity_in_db.update_entity(entity_mapped_to_db)
                # All relations must be removed and added
                # entity_in_db = self.reset_relations(entity_in_db)
                self.db.session.add(entity_in_db)

            # Is not in DB - Insert
            else:
                self.db.session.add(entity_mapped_to_db)

            self.erp_entity.range_next()

        # Here we set the attribute/field of dataset_NAME_sync_date by the entity_name
        # We need to set it BEFORE the sync. So we can query the db for the last sync session
        # by range last_sync - now()
        setattr(self.bridge_synchronize_entity, 'dataset_' + self.entity_name + '_sync_date', datetime.now())
        self.db.session.add(self.bridge_synchronize_entity)

        # Commit everything
        self.db.session.commit()

    def is_in_db(self):
        """
        Check if the entity is in db. Use the standard ERP id field = 'ArtNr' and standard DB id field = erp_nr for Artikel
        The code example would look like:
        self.bridge_entity.query.filter_by(erp_nr=104014).first()
        erp=104014:
            bridge_entity_index_field = self.erp_entity.get_(self.erp_entity_index_field))
        :return: object
        """
        bridge_entity_index_field = self.bridge_entity_index_field
        if bridge_entity_index_field:
            in_db = eval(
                'self.bridge_entity.query.filter_by(erp_nr=self.erp_entity.get_(self.erp_entity_index_field)).first()')
            return in_db
        else:
            return None

    def get_erp_entity(self):
        if self.erp_entity:
            return self.erp_entity
