import attrs
from attrs import validators


@attrs.define
class ConfShopware6ApiBase(object):
    shopware_admin_api_url: str = "http://localhost/api"
    shopware_storefront_api_url: str = "http://localhost/store-api"

    username: str = "admin"
    password: str = "shopware"


    grant_type: str = "user_credentials"



class ShopwareAPIError(BaseException):
    pass