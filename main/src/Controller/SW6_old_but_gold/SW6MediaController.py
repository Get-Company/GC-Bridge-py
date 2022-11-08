from main.src.Controller.SW6_old_but_gold.SW6ObjectController import SW6ObjectController
from main.src.Entity.Bridge.Product import BridgeProductEntity
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import lru_cache
import hashlib
from os import PathLike
from lib_shopware6_api_base import lib_shopware6_api_base_criteria as dal
from main.src.Controller.SW6_old_but_gold.extended.SubMedia import SubMedia
from main.src.Controller.SW6_old_but_gold.extended.SubProduct import SubProduct, SubProductPicture
import json

PathMedia = Union[str, PathLike, pathlib.Path]
PathMediaFolder = Union[str, PathLike, pathlib.Path]


class SW6MediaController(SW6ObjectController):
    def __init__(self):
        self.entity_name = "media"
        self.entity_check_field = "id"
        self.entity_instance = None
        self.api_sub_instance_product = SubProduct()
        self.api_sub_instance_product_picture = SubProductPicture
        self.class_name = "SW6MediaController"

        super().__init__(
            entity_name=self.entity_name,
            entity_instance=self.entity_instance,
            entity_check_field=self.entity_check_field,
            class_name=self.class_name
        )

    def upsert_product_images_to_sw6(self, ntt: BridgeProductEntity):
        self.print_method_info(self.class_name)
        # First delete
        images_db = json.loads(ntt.image)
        position = 10
        pictures = list()

        for image in images_db:
            media = images_db[image]
            if media != 0:
                url = 'https://www.classei.de/images/products/' + media

                pictures.append(self.api_sub_instance_product_picture(
                    position=position,
                    url=url,
                    media_alt=ntt.description,
                    media_title=media,
                ))
                position += 10

        self.api_sub_instance_product.upsert_product_pictures(
            product_number=ntt.erp_nr,
            l_product_pictures=pictures
        )