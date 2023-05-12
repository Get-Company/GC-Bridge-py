from main.src.Controller.SW5_2.SW5_2ObjectController import SW5_2ObjectController
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from pprint import pprint


class SW5_2CustomerObjectController(SW5_2ObjectController):
    def __init__(self):

        super().__init__()

    def delete_duplicates_by_adrnr(self, adrnr):
        double_customers_by_adrnr = SW5_2CustomerObjectEntity().get_all_customers_by_adrnr(adrnr)
        email_adrnr_list = []
        for customer in double_customers_by_adrnr:
            customer = SW5_2CustomerObjectEntity().get_customer(customer['id'])
            double_customers_by_email = SW5_2CustomerObjectEntity().get_all_customers_by_email(customer['email'])
            for email_customer in double_customers_by_email:
                email_adrnr_list.append([
                    email_customer['email'],
                    email_customer['number'],
                    email_customer['id']
                ])

        unique_email_adrnr_list = list(set(map(tuple, email_adrnr_list)))
        pprint(unique_email_adrnr_list)

