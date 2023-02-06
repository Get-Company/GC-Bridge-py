from payload import Payload

class Product(Payload):
    def __init__(self, db_row):
        payload = {
            "id": db_row.api_id,
            "name": db_row.name,
            "createdAt": db_row.erp_ltz_aend.strftime("%Y-%m-%d %H:%M:%S"),
            "productNumber": db_row.erp_nr,
            "stock": db_row.stock,
            "categories": [],
            "taxId": "b5c13f572d1a49a5906a9c300abd28b9",
            "price": [
                {
                    "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
                    "gross": db_row.price * 1.19,
                    "net": db_row.price,
                    "linked": False
                }
            ]
        }
        super().__init__(self, payload)