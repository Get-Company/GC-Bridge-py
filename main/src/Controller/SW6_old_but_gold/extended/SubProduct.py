# STDLIB
from decimal import Decimal
from functools import lru_cache
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union

# EXT
import attrs
from main.src.Controller.SW6_old_but_gold.extended.SubMedia import SubMedia

# OWN
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, ShopwareAPIError, ConfShopware6ApiBase, PayLoad
from lib_shopware6_api_base import lib_shopware6_api_base_criteria as dal

from lib_shopware6_api.sub_product import Product, ProductPicture

import inspect


@attrs.define
class SubProductPicture:
    """
    dataclass to upsert a picture
    """

    # ProductPicture}}}
    position: int = 0  # the position in the shop
    url: str = ""  # the url to upload from
    media_alt: Optional[str] = None  # optional picture alt
    media_title: Optional[str] = None  # optional picture title
    upload_media: bool = True  # if to upload the media (default= True)


class SubProduct(Product):
    def __init__(self):
        super().__init__(use_docker_test_container=True)
        self.media = SubMedia()

    def upsert_product_pictures(self, product_number: Union[int, str], l_product_pictures: List[ProductPicture]) -> None:
        print('\n#- %s %s -#' % ("SubProduct", inspect.currentframe().f_back.f_code.co_name))
        product_id = self.get_product_id_by_product_number(product_number=product_number)
        self.delete_product_media_relations_by_product_number(product_number=product_number)

        l_product_pictures = sorted(l_product_pictures, key=lambda picture: picture.position)

        is_cover_picture = True
        for product_picture in l_product_pictures:
            media_id = self.media.upsert_media(
                product_number=product_number,
                position=product_picture.position,
                url=product_picture.url,
                media_alt=product_picture.media_alt,
                media_title=product_picture.media_title,
                upload_media=True,
            )
            media_relation_id = self.insert_product_media_relation(product_id=product_id, media_id=media_id,
                                                                   position=product_picture.position)

            if is_cover_picture:
                self._update_product_payload(product_id=product_id, payload={"coverId": media_relation_id})
                is_cover_picture = False