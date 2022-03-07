# Github Repository
# https://github.com/bitranox/lib_shopware6_api
from lib_shopware6_api import Shopware6API
from lib_shopware6_api_base import Shopware6AdminAPIClientBase

from config import ConfShopware6ApiBase

from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Controller.SW6.SW6CategoryController import *


def SW6_test():
    my_conf = ConfShopware6ApiBase()
    my_api = Shopware6API(use_docker_test_container=True)

    admin_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)

    # Currency
    # my_api_currency = my_api.currency
    # my_currency_id = my_api_currency.get_currency_id_by_iso_code('EUR')

    # Product
    # my_api_product = my_api.product
    # product = my_api_product.get_product_id_by_product_number('SWDEMO10007')
    #
    # print(product)

    # Category

    ntt = BridgeCategoryEntity.query.filter_by(erp_nr=11).first()
    print(ntt.erp_ltz_aend)
    payload = {
        "id": ntt.api_id,
        "name": ntt.translations[0].title,
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "parent_id": ntt.api_idparent,
        "displayNestedProducts": True,
        "productAssignmentType": "product",
        "type": "page",
    }
    admin_client.request_post("category", payload)


def upsert_category_payload():
    pass


def sw6_get_product_id_by_product_number(product_number):
    product = sw6_get_product()
    product_id = product.get_product_id_by_product_number(product_number)

    return product_id


def sw6_insert_product(ntt: BridgeProductEntity):
    product = sw6_get_product()
    product_id = product.insert_product(
        name=ntt.name,
        product_number=ntt.api_id,
        stock=ntt.stock,
        price_brutto=ntt.price * 1.19,
        price_netto=ntt.price,
        tax_name='Standard rate',
        currency_iso_code="EUR",
        linked=True
    )

    return product_id



def sw6_get_product():
    api = sw6_get_api()
    product = api.product

    return product



def sw6_get_api():
    """
    During Test use the param use_docker_test_container=True

    If production use "conf" which is imported
    my_api = Shopware6API(conf)
    :return:
    """
    api = Shopware6API(use_docker_test_container=True)

    return api
