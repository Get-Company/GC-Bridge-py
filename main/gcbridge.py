import sqlalchemy

from main import create_app
from flask import render_template, redirect
from flask_migrate import Migrate
import sys
from sqlalchemy import and_
from loguru import logger
"""
######################
Entities
make sure all entities are imported, due to circular imports for example:
- BridgeProductEntity needs BridgeCategoryEntity -
We can not import Cat again
######################
"""
# Synchronize
from main.src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity

# Category
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import BridgeCategoryEntity
from main.src.Entity.ERP.ERPArtikelKategorieEntity import ERPArtikelKategorieEntity

# Customer
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity, BridgeCustomerContactEntity
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity, ERPAnschriftenEntity, ERPAnsprechpartnerEntity
from main.src.Entity.ERP.NestedDataSets.ERPUmsatzEntity import ERPUmsatzEntity

# Product
from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.ERP.ERPArtkelEntity import ERPArtikelEntity

# Tax
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import BridgeTaxEntity

# Media
from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaEntity

# Connection
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity

# Mappei
# Controller
from main.src.Controller.Mappei.parser import *


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

# Hallo Atti

"""
######################
ERP Connection
"""
erp_obj = ERPConnectionEntity()
erp_obj.connect()



# Bridge2ObjectTaxController(erp_obj=erp_obj).sync_all()  # OK!
# Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_all()  # OK!
Bridge2ObjectProductController(erp_obj=erp_obj).sync_range(start=581000, end=581010)  # OK!

# Funktioniert doch, oder?
# Bridge2ObjectCustomerContactController(erp_obj=erp_obj).sync_range(start=10026, end=10100)
# Bridge2ObjectCustomerAddressController(erp_obj=erp_obj).sync_range(start=10026, end=10100)
# Bridge2ObjectCustomerController(erp_obj=erp_obj).sync_range(start=10026, end=10100)


# Atti Zeugs - geht eigentlich ganz gut! Is ok...
# SW6UpdatingController().sync_changed_to_sw('category')
# SW6UpdatingController().sync_changed_to_sw('product')

# tab = BridgeProductEntity().query.filter_by(erp_nr=581000).first()
# print("#########################")
# print('\033[95m###### Test Prints ######\033[0m')
# print("#########################")
# print("Tab 581000 Tax:", tab.tax.description, "Category:", tab.categories[0].title)
# print("#########################")
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

""" 
######################
Migration
######################
"""
migrate = Migrate(app, db)


def initialize_new():
    """
    Steps to take for initializing everything at first start
    :return:
    """
    # - create all the tables:
    # db.create_all()
    # - Set the dates on bridge_sync
    # sync = BridgeSynchronizeEntity().get_entity_by_id_1()
    # sync.dataset_category_sync_date = datetime.now()
    # ...


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

        db.create_all()
        main()

    # localhost:5000
    # !IMPORTANT! Do not use reloader on Threaded Tasks, for it will use up erp licenses
    # app.run(port=5000, debug=True, use_reloader=True)
