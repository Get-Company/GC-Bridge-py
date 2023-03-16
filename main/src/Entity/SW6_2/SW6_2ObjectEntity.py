# from lib_shopware6_api_base import Shopware6AdminAPIClientBase, lib_shopware6_api_base_criteria as dal
from lib_shopware6_api import Shopware6AdminAPIClientBase, dal
from lib_shopware6_api_base import EqualsFilter, RangeFilter, MultiFilter, DateHistogramAggregation

from main.config import ConfShopware6ApiBase
from pprint import pprint
import datetime
# Tools
import uuid
import requests
import datetime

from main.src.Repository.functions_repository import get_current_datetime_and_convert_to_sw6_format

# Config
from main.config import ShopwareConfig as sw6config

# Bridge
from main.src.Entity.Bridge.Orders import BridgeOrderEntity
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity


class SW6_2ObjectEntity:
    def __init__(self):

        my_conf = ConfShopware6ApiBase
        my_api_client = Shopware6AdminAPIClientBase(config=my_conf)

        my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)

        self.api = my_api_client

    """    Category    """

    def get_category(self, id):
        category = self.api.request_get(request_url=f'/category/{id}')
        return category

    def get_categories(self):
        try:
            categories = self.api.request_get(request_url='category')
            if categories:
                return categories
            else:
                return None
        except:
            return False

    def upsert_category(self, category, with_parent=False):
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

    def _create_category(self, category):
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

    def _update_category(self, category):
        payload = {
            "name": category.title,
            "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": category.description
        }
        update_category = self.api.request_patch(request_url=f'/category/{category.api_id}', payload=payload)
        print("Updated Category", category.title)
        return update_category

    def _update_category_with_parent(self, category):
        payload = {
            "parentId": category.api_idparent
        }
        if category.erp_nr_parent > 0:
            patched_category = self.api.request_patch(request_url=f'/category/{category.api_id}', payload=payload)
            print("Patched Category with Parent", category.title, category.api_idparent)
            return patched_category
        else:
            print("No Patch for Category", category.title, category.erp_nr_parent)
            pass

    def delete_category(self, id):
        delete_category = self.api.request_delete(request_url=f'/category/{id}')
        print("Deleted Category", id)
        return delete_category

    def delete_all_categories(self):
        categories = self.get_categories()
        for cat in categories['data']:
            print("Category found:", cat['id'])
            # Standard Category for salesChannel
            if not cat['id'] == 'c9c5084cd0ed4e2da4a5db50234805f9':
                try:
                    self.delete_category(cat['id'])
                except:
                    print("Could not delete Cat ID:", cat['id'])
                    pass
            else:
                print("Main Category - do not delete")

    """    SalesChannel    """

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
            'name': sw6config.SCName,
            'accessKey': sw6config.ACCESS_KEY,
            'active': sw6config.ACTIVE,
            'apiAlias': sw6config.APIALIAS,
            'countryId': sw6config.COUNTRY_DE,
            'createdAt': datetime.datetime.now().isoformat(),
            'currencyId': sw6config.CURRENCY_EU,
            'customerGroupId': sw6config.CUSTOMER_GROUP_DE_B2B,
            'homeEnabled': sw6config.HOME_ENABLED,
            'languageId': sw6config.LANGUAGE_ID_DE_DE,
            'navigationCategoryDepth': sw6config.NAVIGATION_CATEGORY_DEPTH,
            'navigationCategoryId': sw6config.NAVIGATION_CATEGORY_ID,
            'paymentMethodId': sw6config.PAYMENT_INVOICE_DE,
            'shippingMethodId': sw6config.SHIPPING_STANDARD,
            'typeId': sw6config.TYPE_ID,
        }
        new_sales_channel = self.api.request_post(request_url='/sales-channel', payload=payload)
        print("Created Sales Channel", payload)
        return new_sales_channel

    """    Tax    """

    def get_tax(self, id):
        try:
            tax = self.api.request_get(request_url='tax/' + id)
            if tax:
                return tax
            else:
                return None
        except:
            return None

    def get_taxes(self):
        try:
            taxes = self.api.request_get(request_url='tax')
            if taxes:
                return taxes
            else:
                return None
        except:
            return False

    def upsert_tax(self, tax):
        # 1. Check if tax exists
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('id', tax.api_id))
        tax_id_in_sw6 = self.api.request_post('/search-ids/tax', payload=payload)
        # the return is ['data'] and ['total']
        # check for total
        if tax_id_in_sw6['total'] <= 0:
            new_tax = self._create_tax(tax=tax)
            return new_tax
        else:
            update_tax = self._update_tax(tax=tax)
            return update_tax

    def _create_tax(self, tax):
        payload = {
            "id": tax.api_id,
            "taxRate": tax.satz,
            "name": tax.description,
            "position": tax.steuer_schluessel,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        new_tax = self.api.request_post(request_url='/tax', payload=payload)
        print("Created Tax", tax.description)
        return new_tax

    def _update_tax(self, tax):
        # Patch
        payload = {
            "taxRate": tax.satz,
            "name": tax.description,
            "position": tax.steuer_schluessel,
            "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        patched_tax = self.api.request_patch(request_url=f'/tax/{tax.api_id}', payload=payload)
        print("Patched Tax", tax.description)
        return patched_tax

    def delete_tax(self, id):
        delete_tax = self.api.request_delete(request_url=f'/tax/{id}')
        print("Deleted Tax", id)
        return delete_tax

    def delete_all_taxes(self):
        taxes = self.get_taxes()
        for tax in taxes['data']:
            if not tax['id'] == '16d9f10db07d41aba8fb7dda32e4d4a9' \
                    and not tax['id'] == '370a45078c4847038884fbd462967176' \
                    and not tax['id'] == 'a131a847f20846bc831a780286578e83':
                print("Delete Tx", tax['id'])
                self.delete_tax(tax['id'])
            else:
                print("Tax ID is standard - Can not be deleted", '16d9f10db07d41aba8fb7dda32e4d4a9')
                pass

    """    Products    """

    def get_product(self, id):
        try:
            product = self.api.request_get(request_url='product/' + id)
            if product:
                return product
            else:
                return None
        except:
            return None

    def get_products(self):
        try:
            products = self.api.request_get(request_url='product')
            if products:
                return products
            else:
                return None
        except:
            return False

    def upsert_product(self, product):
        # 1. Check if product exists
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('id', product.api_id))
        product_id_in_sw6 = self.api.request_post('/search-ids/product', payload=payload)
        # the return is ['data'] and ['total']
        # check for total
        if product_id_in_sw6['total'] <= 0:
            new_product = self._create_product(product=product)
            return new_product
        else:
            update_product = self._update_product(product=product)
            return update_product

    def _create_product(self, product):
        payload = {
            "id": product.api_id,
            "taxId": product.tax.api_id,
            "price": [
                {
                    "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
                    "net": product.price,
                    "gross": product.price * (product.tax.satz / 100 + 1),
                    "linked": False
                }
            ],
            "productNumber": str(product.erp_nr),
            "stock": 99999,
            "name": str(product.erp_nr) + ' ' + str(product.name),
            "description": product.description,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # for cat in product.categories:
        #     payload["categoryIds"].append(cat.api_id)

        new_product = self.api.request_post(request_url='/product', payload=payload)
        print("Created Product", product.erp_nr, product.name)
        return new_product

    def _update_product(self, product):
        # Patch
        payload = {
            "taxId": product.tax.api_id,
            "price": [
                {
                    "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
                    "net": product.price,
                    "gross": product.price * (product.tax.satz / 100 + 1),
                    "linked": False
                }
            ],
            "productNumber": str(product.erp_nr),
            "stock": 99999,
            "name": str(product.erp_nr) + str(product.name),
            "description": product.description,
            "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # for cat in product.categories:
        #     payload["categoryIds"].append(cat.api_id)

        patched_product = self.api.request_patch(request_url=f'/product/{product.api_id}', payload=payload)
        print("Patched Product", product.erp_nr, product.name)
        return patched_product

    def read_product(self, erp_nr=None, id=None, product=None):
        if erp_nr:
            payload = dal.Criteria()
            payload.filter.append(EqualsFilter('product_number', erp_nr))
            read_product = self.api.request_post('/product', payload=payload)
            return read_product

        elif id:
            read_product = self.api.request_get(request_url=f"/product/{id}")
            return read_product

        elif product:
            read_product = self.api.request_get(request_url=f"/product/{product.api_id}")
            return read_product

        else:
            print("Can not search withaut a value:", "Erp_Nr:", erp_nr, "ID:", id, "Product Entity", product)
            return False

    def delete_product(self, id):
        delete_product = self.api.request_delete(request_url=f'/product/{id}')
        print("Deleted Product", id)
        return delete_product

    def delete_all_products(self):
        products = self.get_products()
        for product in products['data']:
            print("Delete Product", product['id'])
            self.delete_product(product['id'])

    """    CustomerAddress    """

    def get_customer(self, id):
        try:
            customer = self.api.request_get(request_url='customer/' + id)
            if customer:
                return customer
            else:
                return None
        except:
            return None

    def get_new_or_updated_customers(self):
        """
        This function retrieves customer addresses from the Shopware 6 API that have been updated since the last
        synchronization. The return of the payload includes the customer!

        Parameters:
            self (object): The object instance.

        Returns:
            list: A list of customer address dictionaries.
        """

        # Get the date of the last synchronization of customer addresses
        last_sync_date_bridge = BridgeSynchronizeEntity().get_entity_by_id_1().sw6_address_sync_date

        # Create a payload with a filter
        payload = dal.Criteria()
        payload.associations["addresses"] = dal.Criteria(limit=200)
        payload.associations["salutation"] = dal.Criteria(limit=10)
        payload.filter.append(
            MultiFilter("or",
                        [
                            RangeFilter(
                                field="updatedAt",
                                parameters={
                                    'gte': last_sync_date_bridge.strftime("%Y-%m-%dT%H:%M:%S")
                                }
                            ),
                            MultiFilter(
                                "and",
                                [
                                    EqualsFilter(field="updatedAt", value=None),
                                    RangeFilter(
                                        field="createdAt",
                                        parameters={
                                            'gte': last_sync_date_bridge.strftime("%Y-%m-%dT%H:%M:%S")
                                        }
                                    )
                                ]
                            )

                        ]
                        )
        )
        # Send the payload to the Shopware 6 API to retrieve the updated customer addresses
        new_or_updated_customers = self.api.request_post('/search/customer', payload=payload)

        for customer in new_or_updated_customers["data"]:
            for address in customer['addresses']:
                salutation = self.get_salutation(address["salutationId"])
                address["salutation"] = salutation["data"][0]

                country = self.get_country(address["countryId"])
                address["country"] = country["data"]


        # Return the retrieved customer addresses
        return new_or_updated_customers

    def get_customers(self):
        try:
            customers = self.api.request_get(request_url='customer')
            if customers:
                return customers
            else:
                return None
        except:
            return False

    def upsert_customer(self, customer):
        # 1. Check if customer exists
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('id', customer.api_id))
        customer_id_in_sw6 = self.api.request_post('/search-ids/customer', payload=payload)
        # the return is ['data'] and ['total']
        # check for total
        if customer_id_in_sw6['total'] <= 0:
            new_customer = self._create_customer(customer=customer)
            return new_customer
        else:
            update_customer = self._update_customer(customer=customer)
            return update_customer

    def _create_customer(self, customer):
        payload = {
            "id": customer.api_id,
            "groupId": 'cfbd5018d38d41d8adca10d94fc8bdd6',
            "defaultPaymentMethodId": 'cbe26c52514543be850dd524ec715aab',
            "salesChannelId": 'a8a5c40ce38b44d1a4bc894a0f343475',
            "languageId": 'eae7aac7c18f401196face426727954c',
            "defaultBillingAddressId": customer.get_default_billing_address().get_default_contact().api_id,
            "defaultShippingAddressId": customer.get_default_shipping_address().get_default_contact().api_id,
            "customerNumber": str(customer.erp_nr),
            "salutationId": '1676fe16d2a9433c8239c33f671bba33',  # male 'f1e1cbcb66b0426d8b947054e244ad0c' # female
            "firstName": customer.get_default_billing_address().get_default_contact().first_name,
            "lastName": customer.get_default_billing_address().get_default_contact().last_name,
            "email": customer.get_default_billing_address().get_default_contact().email,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if customer.ustid:
            payload["company"] = customer.get_default_billing_address().na2
            # Must be created in Shopware 6 Settings->System->Custom fields
            # payload["customer_company_extension_"] = customer.get_default_billing_address().na3
            payload["vatIds"] = [customer.ustid]

        new_customer = self.api.request_post(request_url='/customer', payload=payload)
        print("Created Customer", customer.erp_nr, payload["firstName"], payload["lastName"])

        return new_customer

    def _update_customer(self, customer):
        # Patch
        payload = {
            "defaultBillingAddressId": customer.get_default_billing_address().api_id,
            "defaultShippingAddressId": customer.get_default_shipping_address().api_id,
            "customerNumber": str(customer.erp_nr),
            "salutationId": '1676fe16d2a9433c8239c33f671bba33',  # male 'f1e1cbcb66b0426d8b947054e244ad0c' # female
            "firstName": customer.get_default_billing_address().contacts[0].first_name,
            "lastName": customer.get_default_billing_address().contacts[0].last_name,
            "email": customer.get_default_billing_address().contacts[0].email,
            "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if customer.ustid:
            payload["company"] = customer.get_default_billing_address().na2
            # Must be created in Shopware 6 Settings->System->Custom fields
            # payload["customer_company_extension_"] = customer.get_default_billing_address().na3
            payload["vatIds"] = [customer.ustid]

        patched_customer = self.api.request_patch(request_url=f'/customer/{customer.api_id}', payload=payload)
        print("Patched Customer", customer.erp_nr, customer.addresses[0].contacts[0].first_name,
              customer.addresses[0].contacts[0].last_name)
        return patched_customer

    def delete_customer(self, id):
        delete_customer = self.api.request_delete(request_url=f'/customer/{id}')
        print("Deleted Customer", id)
        return delete_customer

    def delete_all_customers(self):
        """
        This function deletes all customers from the Shopware 6 API.

        Parameters:
            self (object): The object instance.
        """
        # Get a list of all customers
        customers = self.get_customers()

        # Iterate through the customers and delete each one
        for customer in customers['data']:
            self.delete_customer(customer['id'])

    """    Customer Addresses
    Beware! The customer address is a relation of contact
    each contact gets a address
    """

    def get_customer_address(self, contact_id):
        """
        Returns a customer-address by its id
        :param contact_id:
        :return: customer-address json
        """
        customer_address = self.api.request_get(request_url=f"customer-address/{contact_id}")
        return customer_address

    def get_customer_addresses(self, customer_id):
        """
        Returns all adresses from a given customer_id
        :param customer_id
        :return: customer_adresses json
        """
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('customerId', customer_id))
        customer_addresses = self.api.request_post('/search/customer-address', payload=payload)
        return customer_addresses

    def get_customers_addresses_all(self):
        """
        Returns all addresses in the db
        :return:
        """
        customers_addresses_all = self.api.request_get(("customer-address"))
        return customers_addresses_all

    def get_new_or_updated_customer_addresses(self):
        """
        This function retrieves customer addresses from the Shopware 6 API that have been updated since the last
        synchronization. The return of the payload includes the customer!

        Parameters:
            self (object): The object instance.

        Returns:
            list: A list of customer address dictionaries.
        """

        # Get the date of the last synchronization of customer addresses
        last_sync_date_bridge = BridgeSynchronizeEntity().get_entity_by_id_1().sw6_address_sync_date

        # Create a payload with a filter that searches for customer addresses updated since the last synchronization
        payload = dal.Criteria()
        payload.associations["customer"] = dal.Criteria(limit=10)
        print("Searching for new or Updated Customers.", "updatedAt>=",
              last_sync_date_bridge.strftime("%Y-%m-%dT%H:%M:%S"), "#- OR -#", "updatedAt = None/Null && createdAt >=",
              last_sync_date_bridge.strftime("%Y-%m-%dT%H:%M:%S"))
        payload.filter.append(
            MultiFilter("or",
                        [
                            RangeFilter(
                                field="updatedAt",
                                parameters={
                                    'gte': last_sync_date_bridge.strftime("%Y-%m-%dT%H:%M:%S")
                                }
                            ),
                            MultiFilter(
                                "and",
                                [
                                    EqualsFilter(field="updatedAt", value=None),
                                    RangeFilter(
                                        field="createdAt",
                                        parameters={
                                            'gte': last_sync_date_bridge.strftime("%Y-%m-%dT%H:%M:%S")
                                        }
                                    )
                                ]
                            )

                        ]
                        )
        )
        # Send the payload to the Shopware 6 API to retrieve the updated customer addresses
        updates_sw6_customer_addresses = self.api.request_post('/search/customer-address', payload=payload)

        # Return the retrieved customer addresses
        return updates_sw6_customer_addresses

    def upsert_customer_address(self, contact):
        """
        The customer addresses are created and update by the contacts. Each Address can have many contacts.
        Loop through all contacts and backrelate the address.
        Every Address gets the api_id of the contact! So search the address by the contacts' id
        :param customer_address: obj
        :return:
        """
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('id', contact.api_id))
        customer_address_id_in_sw6 = self.api.request_post('/search-ids/customer-address', payload=payload)
        # the return is ['data'] and ['total']
        # check for total
        if customer_address_id_in_sw6['total'] <= 0:
            print("New Address")
            new_customer_address = self._create_customer_address(contact=contact)
            # return new_customer_address
        else:
            print("Update Address")
            # update_customer = self._update_customer(customer=customer_address)
            # return update_customer

    def _create_customer_address(self, contact):
        # Patch
        try:
            country = self.get_country_by_iso(contact.address.land_ISO2)
            pprint(contact.address.land_ISO2)
        except:
            print("No land iso found for contact:", contact, ". Passing.")
            return False
        payload = {
            "id": contact.api_id,
            "customerId": contact.address.customer.api_id,
            "countryId": country["data"][0]["id"],
            "salutationId": "1676fe16d2a9433c8239c33f671bba33",
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "zipcode": str(contact.address.plz),
            "city": contact.address.city,
            "street": contact.address.str,
            "email": contact.address.email,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            new_customer_address = self.api.request_post(request_url='/customer-address', payload=payload)
            print("Created Customer-Address", contact.erp_nr, contact.first_name,
                  contact.last_name)
            return new_customer_address
        except Exception as e:
            print("Could not Create Customer-Address. Error:\n", e)
            return False

    def _update_customer_address(self, contact):
        # Patch
        try:
            country = self.get_country_by_iso(contact.address.land_ISO2)
        except Exception as e:
            print("No land iso found for contact:", contact, ". Passing. Error:\n", e)
            return False

        payload = {
            "id": contact.api_id,
            "customerId": contact.address.customer.api_id,
            "countryId": country["data"][0]["id"],
            "salutationId": "1676fe16d2a9433c8239c33f671bba33",
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "zipcode": str(contact.address.plz),
            "city": contact.address.city,
            "street": contact.address.str,
            "email": contact.address.email,
            "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if contact.address.customer.ustid:
            payload["company"] = contact.address.na2
            # Must be created in Shopware 6 Settings->System->Custom fields
            # payload["customer_company_extension_"] = customer.get_default_billing_address().na3
        try:
            patched_customer_address = self.api.request_patch(request_url=f'/customer-address/{contact.api_id}',
                                                              payload=payload)
            print("Patched Customer-Address", contact.erp_nr, contact.first_name,
                  contact.last_name)
            return patched_customer_address
        except Exception as e:
            print("Could not update Customer Address. Error:\n", e)
            return False

    def delete_customer_address(self, id):
        customer_address = self.api.request_delete(request_url=f"/customer-address/{id}")
        print("Customer-Address Deleted:", id)
        return customer_address

    def delete_all_customer_addresses(self, customer):
        """
        Deletes all adresses of a given customer
        :param customer:
        :return:
        """
        customers_addresses = self.get_customer_addresses(customer=customer)
        for address in customers_addresses['data']:
            self.delete_customer_address(address['id'])

    def delete_all_customers_addresses(self):
        customer_addresses_all = self.get_customers_addresses_all()
        for address in customer_addresses_all["data"]:
            self.delete_customer_address(id=address["id"])

    """    Countries    """

    def get_countries(self):
        countries = self.api.request_get(request_url="/country")
        return countries

    def get_country(self, id):
        country = self.api.request_get(request_url=f"/country/{id}")
        return country

    def get_country_by_name(self, name):
        """
        Name is the string, wether in German or English (or other installed languages), of the country
        Example: "Deutschland"
        :param name: strg land name
        :return: id
        """
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter('name', name))
        country = self.api.request_post('/search/country-translation', payload=payload)
        return country

    def get_country_by_iso(self, iso):
        """
        Returns the request as an array:
        {'aggregations': [],
         'data': [{'_uniqueIdentifier': '491b3f1900864d599de28fd5f9283609',
                   'active': True,
                   'apiAlias': 'country',
                   'checkVatIdPattern': False,
                   'companyTaxFree': False,
                   'createdAt': '2022-04-06T16:45:22.656+00:00',
                   'currencyCountryRoundings': None,
                   'customFields': None,
                   'customerAddresses': None,
                   'displayStateInRegistration': False,
                   'extensions': {'foreignKeys': {'apiAlias': None, 'extensions': []}},
                   'forceStateInRegistration': False,
                   'id': '491b3f1900864d599de28fd5f9283609',
                   'iso': 'DE',
                   'iso3': 'DEU',
                   'name': 'Germany',
                   'orderAddresses': None,
                   'position': 1,
                   'salesChannelDefaultAssignments': None,
                   'salesChannels': None,
                   'shippingAvailable': True,
                   'states': None,
                   'taxFree': False,
                   'taxFreeFrom': None,
                   'taxRules': None,
                   'translated': {'customFields': [], 'name': 'Germany'},
                   'translations': None,
                   'updatedAt': None,
                   'vatIdPattern': '(DE)?[0-9]{9}',
                   'versionId': None}],
         'total': 1}

        country = self.get_country_by_iso('DE')
        get the id by country["data"][0]["id"]
        :param iso: str Like DE or UK
        :return: request response as array
        """
        payload = dal.Criteria()
        payload.filter.append(EqualsFilter("iso", iso))
        print("Search country", iso)
        try:
            country = self.api.request_post("/search/country", payload=payload)
            return country
        except:
            print("No land by iso:", iso, "found")
            return False

    """
    Orders
    """

    def get_order(self, id):
        order = self.api.request_get(request_url=f"order/{id}")
        return order

    def get_orders(self):
        orders = self.api.request_get(request_url="/order")
        return orders

    """
    Customer Group
    """

    def get_salutation(self, id):
        # Create a payload with a filter
        payload = dal.Criteria()

        # payload.associations["translated"] = dal.Criteria(limit=10)
        payload.filter.append(
            EqualsFilter(field="id", value=id),
        )
        salutation = self.api.request_post('/search/salutation', payload=payload)
        return salutation

    """
    Bulk Sync
    """

    def bulk_uploads(self, categories):
        payload = [{
            "action": "upsert",
            "entity": "category",
            "payload": []
        }]
        for category in categories:
            payload[0]["payload"].append({
                "id": category.api_id,
                "name": category.title,
                "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "displayNestedProducts": True,
                "productAssignmentType": "product",
                "type": "page",
                "description": category.description,
                "parentId": category.api_idparent
            })

        category_response = self.api.request_post(request_url='/_action/sync', payload=payload)
        print(category_response)