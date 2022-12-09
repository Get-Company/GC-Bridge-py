from pprint import pprint

import sqlalchemy

from main import create_app
from flask import render_template, redirect, request
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

# Category
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.ERP.ERPArtikelKategorieEntity import ERPArtikelKategorieEntity

# Product
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity

# Customer
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, \
    BridgeCustomerAddressEntity, BridgeCustomerContactEntity
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity, ERPAnschriftenEntity, ERPAnsprechpartnerEntity
from main.src.Entity.ERP.NestedDataSets.ERPUmsatzEntity import ERPUmsatzEntity

# Media
from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaEntity

# Order
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity

# Connection
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity

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
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerContactController import \
    Bridge2ObjectCustomerContactController
from main.src.Controller.Bridge2.Customer.Bridge2ObjectCustomerAddressController import \
    Bridge2ObjectCustomerAddressController
# Atti SW6
from main.src.Controller.SW6.SW6UpdatingController import SW6UpdatingController
from main.src.Controller.SW6.SW6InitController import SW6InitController

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
#
# Bridge2ObjectTaxController(erp_obj=erp_obj).sync_all()  # OK!
# Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_all()  # OK!
# Bridge2ObjectProductController(erp_obj=erp_obj).sync_all()  # OK!
#
# Funktioniert doch, oder?
# Bridge2ObjectCustomerContactController(erp_obj=erp_obj).sync_range(start=10026, end=10100)
# Bridge2ObjectCustomerAddressController(erp_obj=erp_obj).sync_range(start=10026, end=10100)
# Bridge2ObjectCustomerController(erp_obj=erp_obj).sync_range(start=10026, end=10100)

api = SW6_2ObjectEntity()
# cat_deutsch = BridgeCategoryEntity().query.filter_by(erp_nr=11).one_or_none()
# api.upsert_category(category=cat_deutsch)
# katalog1 = api.read_categories(id='c9c5084cd0ed4e2da4a5db50234805f9')
# pprint(katalog1)
# lebensmittel = api.read_categories(id='77b959cf66de4c1590c7f9b7da3982f3')
# pprint(lebensmittel)

cats = db.session.query(BridgeCategoryEntity).order_by(BridgeCategoryEntity.erp_nr_parent.asc())
# for cat in cats:
#     api.delete_category(category=cat)
#     api.upsert_category(category=cat)

# for cat in cats:
#     api.upsert_category(category=cat)

for cat in cats:
    api.upsert_category(category=cat, with_parent=True)

# upsert = api.upsert_category(category=cat_deutsch)
# pprint(upsert)
# product = api.get_product('f03694c75251465cae63c0791872a3a4')
# pprint(product)
# customer_in_sw6 = api.get_customer(id='fc98adbcab884f1bbd9100fbf2e8c774')
# pprint(customer_in_sw6)
# customer = BridgeCustomerEntity().query.filter_by(erp_nr='10028').first()
# api.upsert_customer(customer=customer)


# Atti Zeugs - geht eigentlich ganz gut! Is ok...
# sw6controller = SW6I

# erp_obj.close()
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
    """
    ######################
    Syncing
    ######################
    """
    # Categories
    # sync_all_categories()
    # sync_all_changed_categories()

    # Tax
    # sync_all_tax()

    # Products
    # sync_all_changed_products()
    # sync_all_products()

    # Adressen
    # sync_all_addresses()
    # os.system("shutdown /s /t 1")

    # All
    # continuously
    # erp_connect()
    # while True:
    #    sync_all_continuously(False)
    # erp_close()

    # sync_all_to_db()

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

    """
    ######################
    Flask Server
    ######################
    """

    # Standard Route for index
    @app.route('/')
    def index():
        return render_template('themekitb5.html')

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
        print(mappei_products)
        return render_template('mappei/index.html', mappei_products=mappei_products)

    @app.route('/customer/<adrnr>')
    def show_customer(adrnr):
        try:
            customer = BridgeCustomerEntity().query.filter_by(erp_nr=adrnr).one_or_none()
            return render_template("classei/show_customer.html", customer=customer)
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
    # app.run(port=5000, debug=True, use_reloader=True)
