# STDLIB
from decimal import Decimal
from functools import lru_cache
import hashlib
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

# EXT
import attrs

# OWN
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, ShopwareAPIError, ConfShopware6ApiBase, PayLoad
from lib_shopware6_api_base import lib_shopware6_api_base_criteria as dal

from lib_shopware6_api.sub_media import Media


class SubMedia(Media):
    def __init__(self):
        # CONF
        self.conf_path_media_folder_root = "/Product Media/gc_bridge-python"
        super().__init__(use_docker_test_container=True)

    # calc_media_filename_from_product_number{{{
    @staticmethod
    def calc_media_filename_from_product_number(
            product_number: Union[int, str],
            position: int,
            url: str,
    ) -> str:
        """
        media_filenamescan only exist once - so we build the filename from product_number, position, and extension of the url

        :param product_number:
        :param position:
        :param url:             we take the extension from here
        :return:

        """
        print("SubMedia.calc_media_filename_from_product_number (static)")
        # calc_media_filename_from_product_number}}}
        # media_filename = "{num:0>9}".format(num=str(product_number)) + f"_{position}" + pathlib.Path(url).suffix
        file_url = url

        file_name = str(pathlib.Path(file_url).stem)
        file_suffix = str(pathlib.Path(file_url).suffix)

        file = file_name + file_suffix

        return file

    # calc_path_media_folder_from_product_number{{{
    def calc_path_media_folder_from_product_number(self, product_number: Union[int, str]) -> str:
        """
        get the path of the complete media folder for a given filename.
        the directory structure will be created as follows :
        'xxxx...' the md5-hash buil out of the product number

        conf_path_media_folder_root/xx/xx/xx/xxxxxxxxxxxxxxxxxxxxxxxxxx

        that gives us 16.7 Million directories, in order to spread products evenly in folders (sharding).
        """
        print("SubMedia.calc_path_media_folder_from_product_number")
        file_url = product_number

        file_name = str(pathlib.Path(file_url).stem)
        file_suffix = str(pathlib.Path(file_url).suffix)

        file = file_name+file_suffix

        # calc_path_media_folder_from_product_number}}}
        product_number_md5 = hashlib.md5(str(file).encode("utf-8")).hexdigest()
        path_media_folder = pathlib.Path(self.conf_path_media_folder_root)
        path_media_folder = path_media_folder / \
                            product_number_md5[0:2] / \
                            product_number_md5[2:4] / \
                            product_number_md5[4:6] / \
                            product_number_md5[6:]
        return path_media_folder.as_posix()

    def upsert_media(
        self,
        product_number: Union[int, str],
        position: int,
        url: str,
        media_alt: Union[str, None] = None,
        media_title: Union[str, None] = None,
        upload_media: bool = True,
    ) -> str:
        """
        We need to keep the filename. All shared images would be renamed and uploaded for every single image.
        So we give away the media_title as th product_number.
        The called method "self.calc_path_media_folder_from_product_number" is overwritten to!
        :param product_number:
        :param position:
        :param url:
        :param media_alt:
        :param media_title:
        :param upload_media:
        :return:
        """
        print("SubMedia.upsert_media")
        # The method "self.calc_media_filename_from_product_number" is overwritten:
        media_filename = self.calc_media_filename_from_product_number(product_number=product_number, position=position, url=url)
        # The method "self.calc_path_media_folder_from_product_number" is overwritten:
        path_media_folder = self.calc_path_media_folder_from_product_number(product_number=url)
        media_folder_id = self.upsert_media_folders_by_path(path_media_folder=path_media_folder)

        if self.is_media_existing(media_filename=media_filename):
            media_id = self.update_media(
                media_folder_id=media_folder_id,
                url=url,
                media_alt_txt=media_alt,
                media_title=media_title,
                media_filename=media_filename,
                upload_media=upload_media,
            )
        else:
            media_id = self.insert_media(
                media_folder_id=media_folder_id,
                url=url,
                media_alt_txt=media_alt,
                media_title=media_title,
                media_filename=media_filename,
                upload_media=upload_media,
            )
        return media_id
