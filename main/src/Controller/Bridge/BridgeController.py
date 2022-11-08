"""

This controller takes care of all the actions
http://www.kammerl.de/ascii/AsciiSignature.php

"""
from main.src.Controller.ERP.ERPController import *
from main.src.Controller.Bridge.BridgeObjectProductController import BridgeObjectProductController as Product
from main.src.Controller.Bridge.BridgeObjectCategoryController import BridgeObjectCategoryController as Category
from main.src.Controller.Bridge.BridgeObjectAddressController import BridgeObjectAddressController as Adresse
from main.src.Controller.Bridge.BridgeObjectTaxController import BridgeObjectTaxController as Tax

from main.src.Controller.SW6.SW6InitController import SW6InitController
from main.src.Controller.SW6.SW6UpdatingController import SW6UpdatingController


def sync_all_continuously(connect=True):
    # 1. Create Connection to ERP
    if connect:
        erp_connect()

    # Sync the categories
    print('''
-----------------------------------------------------------    
_____        _                             _            
/ ____|      | |                           (_)           
| |      __ _ | |_  ___   __ _   ___   _ __  _   ___  ___ 
| |     / _` || __|/ _ \ / _` | / _ \ | '__|| | / _ \/ __|
| |____| (_| || |_|  __/| (_| || (_) || |   | ||  __/\__ ]
\_____|\__,_| \__|\___| \__, | \___/ |_|   |_| \___||___/
                      __/ |                           
                     |___/                            
''')

    Category().dataset_save_changed_to_db()
    print('''
-----------------------------------------------------------
-----------------------------------------------------------
''')

    print('''

_____                  _               _        
|  __ \                | |             | |       
| |__) |_ __  ___    __| | _   _   ___ | |_  ___ 
|  ___/| '__|/ _ \  / _` || | | | / __|| __|/ __|
| |    | |  | (_) || (_| || |_| || (__ | |_ \__ ]
|_|    |_|   \___/  \__,_| \__,_| \___| \__||___/
                                                
''')
    Product().dataset_save_changed_to_db()
    print('''
-----------------------------------------------------------
-----------------------------------------------------------
    ''')

    print('''
         _                             
/\      | |                            
/  \   __| |_ __ ___  ___ ___  ___  ___ 
/ /\ \ / _` | '__/ _ \/ __/ __|/ _ \/ __|
/ ____ \ (_| | | |  __/\__ \__ \  __/\__ |
/_/    \_\__,_|_|  \___||___/___/\___||___/
                                               
    ''')
    Adresse().dataset_save_changed_to_db()

    SW6UpdatingController().sync_changed_to_sw()

    if connect:
        erp_close()


def sync_all_to_db(connect=True):
    sync_all_categories(connect)
    sync_all_products(connect)
    sync_all_addresses(connect)


def sync_all_categories(connect=True):
    if connect:
        erp_connect()

    Category().dataset_save_all_to_db()

    if connect:
        erp_close()


def sync_all_changed_categories(connect=True):
    if connect:
        erp_connect()

    Category().dataset_save_changed_to_db()

    if connect:
        erp_close()


def sync_all_products(connect=True):
    if connect:
        erp_connect()

    Product().dataset_save_all_to_db()

    if connect:
        erp_close()


def sync_all_changed_products(connect=True):
    if connect:
        erp_connect()

    Product().dataset_save_changed_to_db()

    if connect:
        erp_close()


def sync_all_addresses(connect=True):
    if connect:
        erp_connect()

    Adresse().dataset_save_all_to_db()

    if connect:
        erp_close()


def sync_all_changed_addresses(connect=True):
    if connect:
        erp_connect()

    Adresse().dataset_save_changed_to_db()

    if connect:
        erp_close()


def sync_all_tax(connect=True):
    if connect:
        erp_connect()

    Tax().dataset_save_all_to_db()

    if connect:
        erp_close()


def sync_sw6_changed():
    SW6UpdatingController().sync_changed_to_sw()


def sync_sw6_all():
    SW6InitController().init_all()

