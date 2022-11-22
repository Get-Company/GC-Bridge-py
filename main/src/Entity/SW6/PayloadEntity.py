from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity, BridgeAnschriftenEntity, BridgeAnsprechpartnerEntity
#from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaRelations
import random
import string

class PayloadEntity:
    def __init__(self, type: str):
        self._type = type

    def setting_payload(self, db_row: any):
        payload = None
        if self._type == "category":
            payload = {
                "id": db_row.api_id,
                # "name": db_row.translations[0].title,
                "name": db_row.title,
                "createdAt": db_row.erp_ltz_aend.strftime("%Y-%m-%d %H:%M:%S"),
                "displayNestedProducts": True,
                "productAssignmentType": "product",
                "type": "page",
                "description": db_row.description
            }
        elif self._type == "category_with_parent":
            payload = {
                "id": db_row.api_id,
                "name": db_row.title,
                "createdAt": db_row.erp_ltz_aend.strftime("%Y-%m-%d %H:%M:%S"),
                "displayNestedProducts": True,
                "productAssignmentType": "product",
                "type": "page",
                "description": db_row.description,
                "parentId": db_row.api_idparent
            }
        elif self._type == "tax":
            payload = {
                "id": db_row.api_id,
                "steuer_schluessel": db_row.steuer_schluessel,
                "description": db_row.description,
                "satz": db_row.satz
            }
        elif self._type == "product":
            payload = {
                "id": db_row.api_id,
                "name": db_row.name,
                "createdAt": db_row.erp_ltz_aend.strftime("%Y-%m-%d %H:%M:%S"),
                "productNumber": db_row.erp_nr,
                "stock": db_row.stock,
                "categories": [],
                "taxId": "30df9b2306d04d709468d2b918c46c97",
                "price": [
                    {
                        "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
                        "gross": db_row.price * 1.19,
                        "net": db_row.price,
                        "linked": False
                    }
                ]
            }

            for category in db_row.categories:
                payload["categories"].append({"id": category.api_id})

            medias = []
            relation_rows = BridgeMediaRelations.query.where(BridgeMediaRelations.product_id == db_row.id).all()
            for row in relation_rows:
                medias.append(
                    {
                        # "id": row.media.sw6_uuid,
                        "mediaId": row.media.sw6_uuid,
                        # "position": 1
                    }
                )
            if len(medias):
                payload["media"] = medias

        elif self._type == "media":
            payload = {
                "url": f"{db_row.media.media_path}{db_row.media.media_name}"
            }

        elif self._type == "customer":
            customer_id = db_row.adrnr
            billing_id = db_row.re_ansnr
            shipping_id = db_row.li_ansnr
            billing_address_row = BridgeAnschriftenEntity.query.filter_by(adrnr=customer_id, ansnr=billing_id).first()
            if billing_address_row is None: return None
            billing_contact_id = billing_address_row.aspnr
            billing_contact_row = BridgeAnsprechpartnerEntity.query.filter_by(adrnr=customer_id, ansnr=billing_id, aspnr=billing_contact_id).first()
            if billing_contact_row is not None:
                billingAddress = {
                    'firstName': billing_contact_row.vna,
                    'lastName': billing_contact_row.nna,
                    'street': billing_address_row.str,
                    'zipcode': billing_address_row.plz,
                    'city': billing_address_row.city,
                    "countryId": "0dbbc93b2b4b4d18bbe42c94f39b0c82"
                }
            else:
                billingAddress = {
                    'firstName': " ",
                    'lastName': " ",
                    'street': billing_address_row.str,
                    'zipcode': billing_address_row.plz,
                    'city': billing_address_row.city,
                    "countryId": "0dbbc93b2b4b4d18bbe42c94f39b0c82"
                }


            shipping_address_row = BridgeAnschriftenEntity.query.filter_by(adrnr=customer_id, ansnr=shipping_id).first()
            if shipping_address_row is None: return None
            shipping_contact_id = billing_address_row.aspnr
            shipping_contact_row = BridgeAnsprechpartnerEntity.query.filter_by(adrnr=customer_id, ansnr=shipping_id, aspnr=shipping_contact_id).first()
            if shipping_contact_row is not None:
                shippingAddress = {
                    'firstName': shipping_contact_row.vna,
                    'lastName': shipping_contact_row.nna,
                    'street': shipping_address_row.str,
                    'zipcode': shipping_address_row.plz,
                    'city': shipping_address_row.city,
                    "countryId": "0dbbc93b2b4b4d18bbe42c94f39b0c82"
                }
            else:
                shippingAddress = {
                    'firstName': " ",
                    'lastName': " ",
                    'street': shipping_address_row.str,
                    'zipcode': shipping_address_row.plz,
                    'city': shipping_address_row.city,
                    "countryId": "0dbbc93b2b4b4d18bbe42c94f39b0c82"
                }

            email = billing_address_row.email
            firstName = billing_address_row.na2
            if billing_address_row.na3 is not None:
                lastName = billing_address_row.na3
            else:
                lastName = " "
            customerNumber = ""
            for x in range(7):
                customerNumber += random.choice(list(string.ascii_letters + string.digits))
            payload = {
                "customerNumber": customerNumber,
                "groupId": "cfbd5018d38d41d8adca10d94fc8bdd6",
                "salesChannelId": "98432def39fc4624b33213a56b8c944d",
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "defaultPaymentMethodId": "03ed3a0908e34e86bc3fbb6c3d8e3c01",
                "defaultBillingAddress": billingAddress,
                "defaultShippingAddress": shippingAddress
            }
        return payload