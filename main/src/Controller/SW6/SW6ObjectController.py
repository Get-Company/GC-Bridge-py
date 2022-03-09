from lib_shopware6_api import Shopware6AdminAPIClientBase, ConfShopware6ApiBase
from typing import Any, Dict, List, Optional, Tuple, Union

from lib_shopware6_api.sub_product import Product
from lib_shopware6_api.sub_currency import Currency
from lib_shopware6_api.sub_tax import Tax
from lib_shopware6_api.sub_media import Media


class SW6ObjectController:
    def __init__(self,
                 entity,
                 admin_client: Optional[Shopware6AdminAPIClientBase] = None,
                 config: Optional[ConfShopware6ApiBase] = None,
                 use_docker_test_container: bool = True):

        self.product = Product(use_docker_test_container=True)
        self.currency = Currency(use_docker_test_container=True)
        self.tax = Tax(use_docker_test_container=True)
        self.media = Media(use_docker_test_container=True)

        if admin_client is None:
            self._admin_client = Shopware6AdminAPIClientBase(config=config,
                                                             use_docker_test_container=use_docker_test_container)
        else:
            self._admin_client = admin_client

