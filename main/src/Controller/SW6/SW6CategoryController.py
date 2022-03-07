from decimal import Decimal
from functools import lru_cache
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

# Ext
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, ShopwareAPIError, ConfShopware6ApiBase, PayLoad
from lib_shopware6_api_base import lib_shopware6_api_base_criteria as dal

from lib_shopware6_api.sub_currency import Currency # type: ignore # pragma: no cover
from lib_shopware6_api.sub_tax import Tax # type: ignore # pragma: no cover
from lib_shopware6_api.sub_media import Media # type: ignore # pragma: no cover
from lib_shopware6_api.sub_product import Product # type: ignore # pragma: no cover

from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *


class Category(object):
    def __init__(
            self,
            admin_client: Optional[Shopware6AdminAPIClientBase] = None,
            config: Optional[ConfShopware6ApiBase] = None,
            use_docker_test_container: bool = False
    ) -> None:
        """

        :param admin_client:
        :param config:
        :param use_docker_test_container:

        >>> # Setup
        >>> my_api = Category()
        """

        if admin_client is None:
            self._admin_client = Shopware6AdminAPIClientBase(config=config,
                                                             use_docker_test_container=use_docker_test_container)
        else:
            self._admin_client = admin_client

        self.currency = Currency(admin_client=self._admin_client)
        self.tax = Tax(admin_client=self._admin_client)
        self.media = Media(admin_client=self._admin_client)
        self.product = Product(admin_client=self._admin_client)

    def insert_category(
            self,
            ntt: BridgeCategoryEntity
    ) -> str:
        payload = {
            "id": ntt.api_id,
            "name": ntt.translations[0].title,
            "createdAt": ntt.erp_ltz_aend,
            "parent_id": ntt.api_idparent,
            "displayNestedProducts": True,
            "productAssignmentType": "product",
            "type": "page",
        }
        self._admin_client.request_post("category", payload)
        return ntt.api_id




