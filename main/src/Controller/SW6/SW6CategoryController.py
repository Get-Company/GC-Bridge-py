from functools import lru_cache

from main.src.Controller.SW6.SW6ObjectController import *
from lib_shopware6_api import Shopware6AdminAPIClientBase, ConfShopware6ApiBase, dal


from main.src.Entity.SW6.SW6CategoryEntity import *

from datetime import datetime


class SW6CategoryController(SW6ObjectController):

    def __init__(self,
                 admin_client: Optional[Shopware6AdminAPIClientBase] = None,
                 config: Optional[ConfShopware6ApiBase] = None,
                 use_docker_test_container: bool = True):

        if admin_client is None:
            self._admin_client = Shopware6AdminAPIClientBase(config=config,
                                                             use_docker_test_container=use_docker_test_container)
        else:
            self._admin_client = admin_client

        self.config = config

        # Initiate all variables to forward them to super.__init__
        self.entity = "category",

        super().__init__(
            self.entity,
            self._admin_client,
            config=config,
            use_docker_test_container=use_docker_test_container
        )

    # cache_clear_category{{{
    def cache_clear_category(self) -> None:
        """
        Cache of some functions has to be cleared if articles are inserted or deleted
        """
        # cache_clear_product}}}
        self.get_category_id_by_id.cache_clear()

    def insert_ntt(self, ntt):
        payload = {
            "id": ntt.api_id,
            "name": ntt.translations[0].title,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # "parentId": ntt.api_idparent,
            "displayNestedProducts": True,
            "productAssignmentType": "product",
            "type": "page",
        }
        self._admin_client.request_post("category", payload)

    def upsert_ntt(self, ntt, add_parent=True):
        payload = SW6CategoryEntity().map_db_to_sw6(ntt, add_parent=True)

        try:
            category_id_in_db = self.get_category_id_by_id(category_id=ntt.api_id)
            print("Category %s not in SW6. Create." % ntt.title)
            self._update_category_payload(category_id_in_db, payload=payload)
        except FileNotFoundError:
            print("Category %s in SW6. Update." % ntt.title)
            self._insert_category_payload(category_id=ntt.api_id, payload=payload)

        return ntt.api_id

    def _update_category_payload(self, category_id: str, payload: Dict[str, Any]) -> None:
        self._admin_client.request_patch(f"category/{category_id}", payload)

    def _insert_category_payload(self, category_id: str, payload: Dict[str, Any]) -> None:
        self._admin_client.request_post("category", payload)
        self.cache_clear_category()

    @lru_cache(maxsize=None)
    def get_category_id_by_id(self, category_id):
        """

        :param category_id:
        :return:
        """
        payload = dal.Criteria()
        payload.page = 1
        payload.limit = 1
        payload.filter = [dal.EqualsFilter(field="id", value=category_id)]

        # Restrict the fields we want to have. Here we just need the id
        payload.includes = {"category": ["id"]}

        dict_response = self._admin_client.request_post(request_url="search/category", payload=payload)
        try:
            article_id = str(dict_response["data"][0]["id"])
            self.get_category_id_by_id.cache_clear()
        except IndexError:
            raise FileNotFoundError(f'category with id "{category_id}" not found')
        return article_id

    def sync_all_categories_from_db_to_sw6(self):
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
