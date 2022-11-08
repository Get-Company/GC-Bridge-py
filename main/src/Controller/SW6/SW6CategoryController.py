from functools import lru_cache

from main.src.Controller.SW6.SW6ObjectController import *
# from lib_shopware6_api import Shopware6AdminAPIClientBase, ConfShopware6ApiBase, dal

from main.src.Entity.SW6.SW6CategoryEntity import *

from datetime import datetime


class SW6CategoryController(SW6ObjectController):
    def __init__(self):

        # Initiate all variables to forward them to super.__init__
        self.entity_name = "category"
        self.entity_check_field = "id"
        self.entity_instance = SW6CategoryEntity()
        self.class_name = "SW6ProductController"

        super().__init__(
            entity_name=self.entity_name,
            entity_instance=self.entity_instance,
            entity_check_field=self.entity_check_field,
            class_name=self.class_name
        )

    def db_save_all_to_sw6(self):
        """
        For the 1. Sync, we need to sync all the categories to sw6, but without the parent.
        When a category is synced with a parent and it doesn't already exist in sw6, we get an error.

        So to sync all properly we need 2 syncs. First all the Categories - then again but with their parent
        :param add_parent:
        :return:
        """
        # 1. Sync without parent. Just simply add all the categories to sw6
        categories_in_db = BridgeCategoryEntity.query.all()
        print("First Sync without parent.")
        for category in categories_in_db:
            self.upsert_ntt(category, add_parent=False)

        # 2. Sync but with the parent. Now we get all the relations
        print("Second Sync with the parent")
        for category in categories_in_db:
            self.upsert_ntt(category, add_parent=True)

        return True

