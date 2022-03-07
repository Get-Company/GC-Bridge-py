"""

This controller takes care of all the actions
http://www.kammerl.de/ascii/AsciiSignature.php

"""
import collections
import uuid
import sys
import time

from sqlalchemy.orm import joinedload
import inspect

from datetime import datetime, timedelta
from main.src.Controller.ERP.ERPController import *
from main.src.Controller.Bridge.BridgeObjectProductController import BridgeObjectProductController as Product
from main.src.Controller.Bridge.BridgeObjectCategoryController import BridgeObjectCategoryController as Category
from main.src.Controller.Bridge.BridgeObjectAddressController import BridgeObjectAddressController as Adresse
# from main.src.Controller.SW6.SW6Controller import *
# Testing
from main.src.Entity.Mappei.MappeiProductEntity import *
from main.src.Entity.Mappei.MappeiPriceEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
from datetime import datetime, timedelta
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import *
from main.src.Controller.Mappei.MappeiController import *
from main.src.Controller.Amazon.AmazonController import *
from main.src.Controller.SW6.SW6Controller import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *


def sync_all_continuously():
    # Set the max recursion limit to
    # 1. Create Connection to ERP
    # erp_connect()

    while True:
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

        # Last
        # erp_close()

        # Call Loop
        # sync_all_continuously()
        return True


def sync_all_categories():
    erp_connect()
    Category().dataset_save_all_to_db()
    erp_close()


def sync_all_changed_categories():
    erp_connect()
    Category().dataset_save_changed_to_db()
    erp_close()


def sync_all_products():
    erp_connect()
    Product().dataset_save_all_to_db()
    erp_close()


def sync_all_changed_products():
    erp_connect()
    Product().dataset_save_changed_to_db()
    erp_close()


def sync_all_addresses():
    erp_connect()
    Adresse().dataset_save_all_to_db()
    erp_close()


def sync_all_changed_addresses():
    erp_connect()
    Adresse().dataset_save_changed_to_db()
    erp_close()


"""
From this line on, TESTS
"""


def tests():
    SW6_test()
