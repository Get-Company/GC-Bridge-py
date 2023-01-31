import csv
import time
from io import StringIO
from pprint import pprint

import sqlalchemy

from main import create_app
from flask import render_template, redirect, request, make_response
from flask_migrate import Migrate
import sys
from sqlalchemy import and_
from loguru import logger

from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity

"""
######################
Entities
make sure all entities are imported, due to circular imports for example
######################
"""
# Synchronize
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

# Tax
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity
from main.src.Entity.ERP.NestedDataSets.ERPNestedDatasetObjectEntity import ERPNestedDatasetObjectEntity

# Category
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.ERP.ERPArtikelKategorieEntity import ERPArtikelKategorieEntity

# Product
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity

# Customer
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, \
    BridgeCustomerAddressEntity
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity, ERPAnschriftenEntity, ERPAnsprechpartnerEntity
from main.src.Entity.ERP.NestedDataSets.ERPUmsatzEntity import ERPUmsatzEntity

# Media
from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaEntity

# Order
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity

# History
from main.src.Entity.ERP.ERPHistoryEntity import ERPHistoryEntity

# Connection
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity

# Misc
from main.src.Entity.Bridge.Misc.BridgeCurrencyEntity import BridgeCurrencyEntity

# Mappei

# Controller
from main.src.Controller.Mappei.parser import *

# SW6
from main.src.Entity.SW6_2.SW6_2ObjectEntity import SW6_2ObjectEntity

"""
######################
Controller
######################
"""
from main.src.Controller.Bridge2.Bridge2ObjectTaxController import Bridge2ObjectTaxController
from main.src.Controller.Bridge2.Bridge2ObjectCategoryController import Bridge2ObjectCategoryController
from main.src.Controller.Bridge2.Bridge2ObjectProductController import Bridge2ObjectProductController
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerController import Bridge2ObjectCustomerController
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerAddressController import \
    Bridge2ObjectCustomerAddressController

from main.src.Controller.Bridge2.Misc.Bridge2ObjectCurrencyController import Bridge2ObjectCurrencyController

# ERP
from main.src.Controller.ERP.ERPCustomerController import ERPCustomerController

# Atti SW6
from main.src.Controller.SW6.SW6UpdatingController import SW6UpdatingController
from main.src.Controller.SW6.SW6InitController import SW6InitController

# Amazon
from main.src.Controller.Amazon.AmazonController import AmazonController

# SW6_2
from main.src.Controller.SW6_2.SW6_2ControllerObject import SW6_2ControllerObject

"""
######################
Tests
#######################
"""
"""
######################
App Factory
The context has to be pushed to app, to grant access to the db's
######################
"""
app = create_app()
app.app_context().push()

""" 
######################
Migration
######################
"""
migrate = Migrate(app, db)

"""
######################
ERP Connection
"""
# erp_obj = ERPConnectionEntity()
# erp_obj.connect()

# ERP
# address = ERPAdressenEntity(erp_obj=erp_obj).find_("10026")
# print(address.get_("AdrNr"))

# Bridge2ObjectTaxController(erp_obj=erp_obj).sync_all()
# Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_all()
# Bridge2ObjectProductController(erp_obj=erp_obj).sync_all()

# erp_obj_test = ERPConnectionEntity(mandant="TEST")
# erp_obj_test.connect()
# ERPCustomerController(erp_obj=erp_obj_test).sync_range_upsert(start="10000", end="10000")
# ERPCustomerController(erp_obj=erp_obj_test).sync_changed_upsert()
# ERPCustomerController(erp_obj=erp_obj_test).sync_changed_downsert()
# erp_obj_test.close()

# ERPCustomerController(erp_obj=erp_obj).sync_range(start=10026, end=10100)

# Bridge2ObjectCustomerAddressController(erp_obj=erp_obj).sync_range(start=10026, end=10026)
# Bridge2ObjectCustomerController(erp_obj=erp_obj).sync_range(start=10026, end=10030)
# Bridge2ObjectCustomerController(erp_obj=erp_obj).sync_changed()


# SW6 Flo
# SW6_2ControllerObject().create_saleschannels()
# SW6_2ControllerObject().insert_init()
# SW6_2ControllerObject().upsert_taxes()
# SW6_2ControllerObject().upsert_categories()
# SW6_2ControllerObject().upsert_products()
# SW6_2ControllerObject().sync_customers(erp_obj=erp_obj)
# SW6_2ControllerObject().upsert_customer_address(10026)
# SW6_2ControllerObject().sync_orders()

# synchronize_bridge = BridgeSynchronizeEntity().get_entity_by_id_1()
# synchronize_bridge.dataset_address_sync_date
# records = BridgeCustomerEntity.query.filter(
#     (BridgeCustomerEntity.erp_nr == 10030) &
#     (BridgeCustomerEntity.erp_nr <= 10050) &
#     ((BridgeCustomerEntity.created_at < synchronize_bridge.dataset_address_sync_date) &
#      (BridgeCustomerEntity.updated_at < synchronize_bridge.dataset_address_sync_date))
# ).all()
#
# pprint(records)

# Atti Zeugs
# sw6controller = SW6I

# erp_obj.close()

"""
######################
Mappei
######################
"""
# get_products_list()


"""
######################
Threaded 
######################

def sync_thread():
    threaded_app = create_app()
    threaded_app.app_context().push()
    erp_obj = ERPConnectionEntity()
    erp_obj.connect()
    while True:
        Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_changed()
        Bridge2ObjectProductController(erp_obj=erp_obj).sync_changed()


t1 = threading.Thread(target=sync_thread)
t1.start()
"""


def main():
    # erp_obj = ERPConnectionEntity()
    # erp_obj.connect()
    """
    ######################
    Syncing
    ######################
    """
    # bridge = BridgeSynchronizeEntity()
    # bridge.id=1
    # bridge.dataset_category_sync_date = datetime.now()
    # bridge.dataset_product_sync_date = datetime.now()
    # bridge.dataset_address_sync_date = datetime.now()
    # bridge.dataset_tax_sync_date = datetime.now()
    # bridge.dataset_order_sync_date = datetime.now()
    # bridge.sw6_category_sync_date = datetime.now()
    # bridge.sw6_product_sync_date = datetime.now()
    # bridge.sw6_address_sync_date = datetime.now()
    # bridge.sw6_order_sync_date = datetime.now()
    # db.session.add(bridge)
    # db.session.commit()

    # Tax
    # Bridge2ObjectTaxController(erp_obj=erp_obj).sync_all()  # OK!
    # sync_all_tax()

    # Categories
    # Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_all()  # OK!
    # sync_all_categories()
    # sync_all_changed_categories()

    # Products
    # Bridge2ObjectProductController(erp_obj=erp_obj).sync_all()  # OK!
    # sync_all_changed_products()
    # sync_all_products()

    # Adressen
    # Bridge2ObjectCustomerAddressController(erp_obj=erp_obj).sync_range(start=10026, end=10100)
    # Bridge2ObjectCustomerController(erp_obj=erp_obj).sync_range(start=10026, end=10100)

    # History
    # erp_history = ERPHistoryEntity(erp_obj=erp_obj)

    # sync_all_addresses()
    # os.system("shutdown /s /t 1")

    # All
    # continuously
    # erp_connect()
    # while True:
    #    sync_all_continuously(False)
    # erp_close()

    # sync_all_to_db()

    # erp_obj.close()
    """
    ######################
    Tests
    ######################
    """
    # tests()

    """
    ######################
    Mappei
    ######################
    When activated it asks you in the CLI if you want to download and save the xml,
    then reads the xml with parse and xmlreader and saves all information in the db
    """
    # This is just a CLI Version which awaits input
    # get_products_list()
    # products = MappeiProductEntity.query.filter(MappeiProductEntity.prices[.has(land="ch"))
    # products = MappeiProductEntity.query.join(MappeiProductEntity)
    # pprint(products)

    """
    ######################
    Flask Server
    ######################
    """

    @app.route('/')
    def index():
        return render_template('themekitb5.html')

    # Dashboard
    @app.route('/dashboard/')
    def index_dashboard():
        print('Dashboard')
        return render_template('dashboard/index.html')

    @app.route('/dashboard/last_sync/products')
    def dashboard_last_sync_products():
        # 1 Query for products range by bridge_synchronize_entity
        last_product_sync = BridgeSynchronizeEntity().get_entity_by_id_1().dataset_product_sync_date

        bridge_product_entity = BridgeProductEntity()
        specific_date = datetime.datetime(2022, 9, 15, 10, 23, 23)
        products = bridge_product_entity.query.filter(
            bridge_product_entity.id.between(
                100, 102)
        ).all()
        print(type(products[0].erp_ltz_aend), products[0].erp_ltz_aend)
        return products[0].erp_ltz_aend

    @app.route('/mappei/all')
    def show_mappei_products_all():
        mappei_products = MappeiProductEntity.query.all()
        return render_template('mappei/index.html', mappei_products=mappei_products)

    @app.route('/mappei/<land>')
    def show_mappei_products_(land: str):
        mappei_products = MappeiProductEntity.query.all()
        return render_template('mappei/index.html', mappei_products=mappei_products, land=land)

    @app.route('/customers')
    def show_customers():
        customers = BridgeCustomerEntity().query.all()
        return render_template('classei/customer/customers.html', customers=customers)

    @app.route('/customer/<customer_id>')
    def show_customer(customer_id):
        try:
            customer = BridgeCustomerEntity().query.get(customer_id)
            return render_template("classei/customer/customer_details.html", customer=customer)
        except sqlalchemy.exc.MultipleResultsFound:
            return redirect("/dashborad")

    @app.route('/classei/price_raise')
    def show_classei_products():
        classei_products = BridgeProductEntity.query.order_by(BridgeProductEntity.erp_nr).all()
        for classei in classei_products:
            if classei.mappei.count():
                m_price = classei.mappei[0].get_normal_price()
                difference = (m_price - classei.price) / classei.price * 100
                classei.difference = difference

        return render_template('/classei/price_raise.html', classei_products=classei_products)


# EOF main


""" 
######################
Server
######################
"""
# check if we are in the main Script? Thread? Check for __main__
if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()
        main()

    # localhost:5000
    # !IMPORTANT! Do not use reloader on Threaded Tasks, for it will use up erp licenses
    app.run(port=5000, debug=True, use_reloader=True)
