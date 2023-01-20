import os
# Make the path to Project/db
BASE_DIR = os.path.dirname(os.path.abspath(__name__))


class Config:
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    #     os.path.join(BASE_DIR, 'db/gc-bridge_python.db')

    #  XAMPP Mysql DB
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/gc-bridge_python'

    #  Docker localhost:3306
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:password@localhost:3306/gc-bridge_db'


    SQLALCHEMY_TRACK_MODIFICATIONS = False


class MappeiConfig:
    mappei_shop_url = "https://shop.mappei.de"
    de = "de"
    at = "at"
    ch = "ch"
    sitemap = "sitemap.xml"
    mappei_de_sitemap = mappei_shop_url + "/" + sitemap
    mappei_at_sitemap = mappei_shop_url + "/" + at + "/" + sitemap
    mappei_ch_sitemap = mappei_shop_url + "/" + ch + "/" + sitemap


import attrs
from attrs import validators


@attrs.define
class ConfShopware6ApiBase(object):
    # the api url, like : 'https://shop.yourdomain.com/api'
    shopware_admin_api_url: str = "http://localhost/api"
    # the storefront api url, like : 'https://shop.yourdomain.com/store-api'
    shopware_storefront_api_url: str = ""

    """
    Admin API:
    for User Credentials Grant Type:
    ==================================
    - with refresh token
    - we recommend to only use this grant flow for client applications that should
      perform administrative actions and require a user-based authentication

    """
    username: str = "admin"
    password: str = "shopware"

    """
    Admin API:
    for Resource Owner Password Grant Type:
    =======================================
    - no refresh token
    - should be used for machine-to-machine communications, such as CLI jobs or automated services
    see https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
    setup via Web Administration Interface > settings > system > integration: "access_id" and "access_secret"
    or directly via URL : https://<fqdn>/admin#/sw/integration/index
    were <fqdn> is the fully qualified domain name, like https://myshop.mydomain.com/admin#/sw/integration/index
    """
    # the client key ID, setup at Web Administration Interface > settings > system > integration > access_id
    client_id: str = "SWIAZMPJQW1JWGLYSMJTWXLWTA"
    # the client secret, setup at Web Administration Interface > settings > system > integration > access_secret
    client_secret: str = "dFNOT3F5dFRremhETFc3TWdrN00zZVBtdFBQQVZYTmFhWGxKYzA"

    """
    Admin API:
    Grant Type to use:
    ==================
    which grant type to use - can be either 'user_credentials'- or 'resource_owner'
    """
    grant_type: str = "user_credentials"

    """
    Store API:
    sw-access-key set in Administration/Sales Channels/API
    """
    store_api_sw_access_key: str = ""


class ShopwareConfig:

    SCName = 'Kunden DE B2B'
    LANGUAGE_ID_DE_DE = 'eae7aac7c18f401196face426727954c'
    LANGUAGE_ID_EN_GB = '2fbb5fe2e29a4d70aa5854ce7ce3e20b'
    CUSTOMER_GROUP_DE_B2B = '4e2ea6b1c8cf474cb05bebf4c6a7da26'
    CURRENCY_EU = 'b7d2554b0ce847cd82f3ac9bd1c0dfca'
    PAYMENT_INVOICE_DE = 'cbe26c52514543be850dd524ec715aab'
    SHIPPING_STANDARD = '3644c4baea6b48a19a9da54af8d07083'
    COUNTRY_DE = '491b3f1900864d599de28fd5f9283609'
    NAVIGATION_CATEGORY_ID = 'eb53e2dac7e843dc91a2766e22a6a49f'
    NAVIGATION_CATEGORY_DEPTH = 3
    NAME = 'Germany - Deutsch'
    ACCESS_KEY = 'SWIAZMPJQW1JWGLYSMJTWXLWTA'
    HOME_ENABLED = True
    ACTIVE = True
    APIALIAS = 'sales_channel'
    TYPE_ID = '8a243080f92e4c719546314b577cf82b'
