# from lib_shopware6_api_base import Shopware6AdminAPIClientBase, lib_shopware6_api_base_criteria as dal
from lib_shopware6_api import Shopware6AdminAPIClientBase, dal
from lib_shopware6_api_base import EqualsFilter

from main.config import ConfShopware6ApiBase
from pprint import pprint
import datetime
# Tools
import uuid

from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Repository.functions_repository import get_current_datetime_and_convert_to_sw6_format

# Config
from main.config import ShopwareConfig as sw6config

# Bridge
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity


class SW6_2ObjectEntity:
    def __init__(self):
        print("SW6_2ObjectEntity Created")

        my_conf = ConfShopware6ApiBase
        my_api_client = Shopware6AdminAPIClientBase(config=my_conf)

        my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)

        self.api = my_api_client

    """
    Order
    """

    def get_orders(self):
        payload = dal.Criteria()
        payload.associations['lineItems'] = dal.Criteria(limit=5)
        payload.associations['orderCustomer'] = dal.Criteria(limit=5)
        orders = self.api.request_post(request_url='search/order', payload=payload)
        pprint(orders)
        return orders

    """
    Category
    """

    def read_categories(self, id):
        read_category = self.api.request_get(request_url=f'/category/{id}')
        return read_category

    def upsert_category(self, category: BridgeCategoryEntity, with_parent=False):
        # 1. Check if category exists
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('id', category.api_id))
        cat_id_in_sw6 = self.api.request_post('/search-ids/category', payload=payload)
        # the return is ['data'] and ['total']
        # check for total
        if cat_id_in_sw6['total'] <= 0:
            new_category = self._create_category(category=category)
            return new_category
        else:
            if not with_parent:
                update_category = self._update_category(category=category)
                return update_category
            else:
                patched_category = self._update_category_with_parent(category=category)
                return patched_category

    def _create_category(self, category: BridgeCategoryEntity):
        payload = {
            "id": category.api_id,
            "name": category.title,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "displayNestedProducts": True,
            "productAssignmentType": "product",
            "type": "page",
            "description": category.description
        }
        new_category = self.api.request_post(request_url='/category', payload=payload)
        print("Created Category", category.title)
        return new_category

    def _update_category(self, category: BridgeCategoryEntity):
        payload = {
            "name": category.title,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "displayNestedProducts": True,
            "productAssignmentType": "product",
            "type": "page",
            "description": category.description
        }
        update_category = self.api.request_put(request_url=f'/category/{category.api_id}', payload=payload)
        print("Updated Category", category.title)
        return update_category

    def _update_category_with_parent(self, category: BridgeCategoryEntity):
        payload = {
            "parentId": category.api_idparent
        }
        if category.erp_nr_parent > 0:
            patched_category = self.api.request_patch(request_url=f'/category/{category.api_id}', payload=payload)
            print("Patched Category", category.title, category.api_idparent)
            return patched_category
        else:
            print("No Patch fo Category", category.title, category.erp_nr_parent)
            pass

    def delete_category(self, category: BridgeCategoryEntity):
        delete_category = self.api.request_delete(request_url=f'/category/{category.api_id}')
        print("Deleted Category", category.title)
        return delete_category

    """
    Customers
    """

    def get_customer(self, id):
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('id', id))
        payload.associations['defaultBillingAddress'] = dal.Criteria(limit=1)
        payload.associations['defaultShippingAddress'] = dal.Criteria(limit=1)
        try:
            customer = self.api.request_post(request_url=f'search/customer', payload=payload)
            return customer
        except:
            print("Customer not found:", id)

    def get_customers(self):
        customers = self.api.request_get(request_url=f'customer')
        return customers

    def upsert_customer(self, customer: BridgeCustomerEntity):
        payload = {
            "groupId": "9263c45bfe2e46a0b48c05e14139d4ad",
            "defaultPaymentMethodId": "cbe26c52514543be850dd524ec715aab",
            "salesChannelId": "cd9a27ea46e840acbf0454e61737cdc4",
            "languageId": "2fbb5fe2e29a4d70aa5854ce7ce3e20b",
            "defaultBillingAddressId": customer.addresses[0].api_id,
            "defaultBillingAddress": [
                {
                    "customerId": customer.api_id,
                    "countryId": "491b3f1900864d599de28fd5f9283609",  # Deutschland
                    "salutationId": "1676fe16d2a9433c8239c33f671bba33",  # Herr, Frau
                    "firstName": customer.addresses[0].contacts[0].first_name,
                    "lastName": customer.addresses[0].contacts[0].last_name,
                    "zipcode": customer.addresses[0].plz,
                    "city": customer.addresses[0].city,
                    "company": customer.addresses[0].company,
                    "street": customer.addresses[0].str,
                    "createdAt": customer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ],
            "defaultShippingAddressId": customer.addresses[0].api_id,
            "customerNumber": str(customer.erp_nr),
            "salutationId": "1676fe16d2a9433c8239c33f671bba33",
            "firstName": customer.addresses[0].contacts[0].first_name,
            "lastName": customer.addresses[0].contacts[0].last_name,
            "email": customer.addresses[0].email,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        pprint(payload)
        new_customer = self.api.request_post(request_url="/customer", payload=payload)
        print("New Customer:", new_customer)

    def find_customer(self, api_id):
        try:
            customer = self.api.request_get(request_url='customer/' + api_id)
            return customer
        except:
            return None

    """
    SalesChannel
    """

    def get_saleschannel(self):
        sales_channels = self.api.request_get(request_url='sales-channel')
        for sc in sales_channels["data"]:
            if sc["name"] == 'Germany - Deutsch':
                pprint(sc)

    def get_saleschannels(self):
        sales_channels = self.api.request_get(request_url='sales-channel')
        for sc in sales_channels["data"]:
            pprint(sc["name"])

    def create_saleschannel(self):
        payload = {
            {'_uniqueIdentifier': 'cd9a27ea46e840acbf0454e61737cdc4',
             'accessKey': sw6config.ACCESS_KEY,
             'active': sw6config.ACTIVE,
             'apiAlias': sw6config.APIALIAS,
             'countryId': sw6config.COUNTRY_DE,
             'createdAt': get_current_datetime_and_convert_to_sw6_format(),
             'currencies': sw6config.CURRENCY_EU,
             'currencyId': sw6config.CURRENCY_EU,
             'customerGroupId': sw6config.CUSTOMER_GROUP_DE_B2B,
             'homeEnabled': sw6config.HOME_ENABLED,
             # 'id': 'cd9a27ea46e840acbf0454e61737cdc4',
             'languageId': sw6config.LANGUAGE_ID_DE_DE,
             'navigationCategoryDepth': sw6config.NAVIGATION_CATEGORY_DEPTH,
             'navigationCategoryId': sw6config.NAVIGATION_CATEGORY_ID,
             'paymentMethodIds': [sw6config.PAYMENT_INVOICE_DE],
             'shippingMethodId': sw6config.SHIPPING_STANDARD,
             'typeId': uuid.uuid4().hex,
             }
        }

    """
    Tax
    """

    def upsert_tax(self):
        try:
            taxes = BridgeTaxEntity.query.all()
            pprint("Taxes", taxes)
            for tax in taxes:
                tax_in_sw6 = self.get_tax(tax.api_id)
                payload = {
                    'taxRate': tax.satz,
                    'name': tax.description,
                    'position': tax.id
                }
                if tax_in_sw6 is not None:
                    try:
                        self._update_tax(id=tax.api_id, payload=payload)
                        return True
                    except:
                        print("Error on Update Tax:", tax.id, tax.description)
                        pass

                elif tax_in_sw6 is None:
                    payload["id"] = tax.api_id
                    self._insert_tax(payload=payload)
        except:
            print("Taxes could not be fetched from Bridge")

    def _update_tax(self, id, payload):
        # Patch
        update_tax = self.api.request_patch(request_url="tax/" + id, payload=payload)
        pprint("Update Tax", payload)
        return True

    def _insert_tax(self, payload):
        insert_tax = self.api.request_post(request_url="tax", payload=payload)
        pprint("Insert Tax", payload)
        return True

    def get_tax(self, id):
        try:
            tax = self.api.request_get(request_url='tax/' + id)
            if tax:
                return tax
            else:
                return None
        except:
            return None

    """
    CustomerGroups
    """

    """
    Products
    """

    def create_product(self, product: BridgeProductEntity):
        payload = {
            "id": product.api_id,
            "name": product.name,
            "productNumber": product.erp_nr,
            "stock": 10,
            "taxId": "e495f3d715a04968bd0820dafe191aa8",
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price": [
                {
                    # Attention Small Caps!!!!!!
                    "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
                    "net": product.price,
                    "linked": True
                }
            ], "cmsPageId": "7a6d253a67204037966f42b0119704d5"
        }

        for cat in product.categories:
            payload["Categories"] = [{
                "id": cat.api_id,
                "name": cat.title,
                "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "displayNestedProducts": True,
                "productAssignmentType": "product",
                "type": "page",
                "description": cat.description
            }]

    def get_product(self, id):
        product = self.api.request_get(f'product/{id}')
        return product
