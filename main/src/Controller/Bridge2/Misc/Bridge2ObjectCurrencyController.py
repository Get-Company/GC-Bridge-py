from main.src.Controller.Bridge2.Bridge2ObjectController import Bridge2ObjectController
from main.src.Entity.Bridge.Misc.BridgeCurrencyEntity import BridgeCurrencyEntity
import requests
from datetime import datetime, timedelta
from main import db
import json

"""
Queries the currency every week on monday
"""


class Bridge2ObjectCurrencyController(Bridge2ObjectController):
    def __init__(self):
        self.api_key = "843NFWCS6Ye0eVfezdK1JdZcAiZU99nD"
        self.bridge_entity = BridgeCurrencyEntity()
        self.currency_iso_3 = "CHF"

    def sync(self):
        need_sync = self.need_sync()

        if need_sync is None:
            # Need Insert
            currency = self.get_curreny_from_api()
            print("Currency ", currency["base"], "will be inserted")
            currency_entity = BridgeCurrencyEntity().map_api_to_bridge(currency)
            db.session.add(currency_entity)
            self.c
        elif need_sync:
            currency = self.get_curreny_from_api()
            print("Currency ", currency["base"], "will be updated from", need_sync.rate, "to", currency["rates"]["EUR"])
            currency_entity = BridgeCurrencyEntity().map_api_to_bridge(currency)
            updated_entity = need_sync.update_entity(currency_entity)
            db.session.add(updated_entity)
            self.commit_with_errors()
        else:
            pass

    def get_curreny_from_api(self):
        url = f"https://api.apilayer.com/fixer/latest?symbols=EUR&base={self.currency_iso_3}"

        payload = {}
        headers = {
            "apikey": self.api_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        status_code = response.status_code
        result = response.text

        # return result
        obj = json.loads(result)
        return obj

    def need_sync(self, currency_iso_3="CHF"):
        is_in_db = self.bridge_entity.query.filter_by(ISO=currency_iso_3).one_or_none()
        if is_in_db:
            now = datetime.now()
            time_diff = now - is_in_db.updated_at

            if time_diff > timedelta(weeks=1):
                return is_in_db
            else:
                datetime
                print("Currency updated on", is_in_db.updated_at.strftime("%d.%m.%Y %H:%M:%S"), "just", time_diff.days,"day(s) ago!")
                return False
        else:
            return None
