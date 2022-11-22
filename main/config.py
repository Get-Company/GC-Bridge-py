import os
# Make the path to Project/db
BASE_DIR = os.path.dirname(os.path.abspath(__name__))
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

"""
Database configuration variables from config.ini
"""
database_server = config['DATABASE']['Server']
database_database = config['DATABASE']['Database']
database_user = config['DATABASE']['User']
database_password = config['DATABASE']['Password']
database_port = config['DATABASE']['Port']
"------------------------------------------------"
"""
Shopware configuration variables from config.ini
"""
shopware_url = config['SHOPWARE']['ShopwareURL']
shopware_user = config['SHOPWARE']['User']
shopware_password = config['SHOPWARE']['Password']



class Config:
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    #     os.path.join(BASE_DIR, 'db/gc-bridge_python.db')

    #  XAMPP Mysql DB
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/gc-bridge_python'

    #  Docker localhost:3306
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{database_user}:{database_password}@{database_server}:{database_port}/{database_database}'


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
    shopware_admin_api_url: str = f"{shopware_url}"
    shopware_storefront_api_url: str = f"{shopware_url}"

    """
    Admin API:
    for User Credentials Grant Type:
    ==================================
    - with refresh token
    - we recommend to only use this grant flow for client applications that should
      perform administrative actions and require a user-based authentication

    """
    username: str = f"{shopware_user}"
    password: str = f"{shopware_password}"

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
    # the client ID, setup at Web Administration Interface > settings > system > integration > access_id
    client_id: str = "SWUAA09NYXBRNXPCUWNQWLHLZW"
    # the client secret, setup at Web Administration Interface > settings > system > integration > access_secret
    client_secret: str = "OTZqZ2tOaUJTYzRDMVFrYmt0UTJtVjlxWm14aGhxTmRLeWZwaHM"

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