from functools import lru_cache

from main.src.Controller.SW6.SW6ObjectController import *
from lib_shopware6_api import Shopware6AdminAPIClientBase, ConfShopware6ApiBase, dal

from main.src.Entity.SW6.SW6ProductEntity import *

from datetime import datetime


class SW6ProductController(SW6ObjectController):
    def __init__(self):

        # Initiate all variables to forward them to super.__init__
        self.api_name = "product"
        self.api_check_field = "id"
        self.api_instance = SW6ProductEntity()

        super().__init__(
            api_name=self.api_name,
            api_instance=self.api_instance,
            api_check_field=self.api_check_field,
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
        products_in_db = BridgeProductEntity.query.all()
        print("First Sync without parent.")
        for product in products_in_db:
            self.upsert_ntt(product, add_parent=False)

        return True

