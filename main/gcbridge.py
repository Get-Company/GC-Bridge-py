import os
from io import StringIO
from pprint import pprint

import html2text
import subprocess
import sqlalchemy
from datetime import datetime, timedelta

from main import create_app
from flask import render_template, redirect, request, make_response
from flask_migrate import Migrate

import sys
from sqlalchemy import and_
from loguru import logger

from datetime import date

# from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import BridgeAdressenEntity
# from main.src.Shopware6Bridge.process import sw6_cus, sw6_order

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

# Price
from main.src.Entity.Bridge.Price.BridgePriceEntity import BridgePriceEntity

# Customer
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity, \
    BridgeCustomerAddressEntity
from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity, ERPAnschriftenEntity, ERPAnsprechpartnerEntity
from main.src.Entity.ERP.NestedDataSets.ERPUmsatzEntity import ERPUmsatzEntity

# Media
from main.src.Entity.Bridge.Media.BridgeMediaEntity import BridgeMediaEntity

# Order
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import BridgeOrderEntity, order_product
from main.src.Entity.Bridge.Orders.BridgeOrderStateEntity import BridgeOrderStateEntity

# History
from main.src.Entity.ERP.ERPHistoryEntity import ERPHistoryEntity

# Connection
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity

# Misc
from main.src.Entity.Bridge.Misc.BridgeCurrencyEntity import BridgeCurrencyEntity

# Mappei

# Controller
from main.src.Controller.Mappei.parser import *

# SW5
# from main.src.Controller.SW5.APIClient import client_from_env, APIClient
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity
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
from main.src.Controller.ERP.ERPOrderController import ERPOrderController

# Atti SW6
# from main.src.SW6_Bridge.process import sw_bridge

# Amazon
from main.src.Controller.Amazon.AmazonController import AmazonController

# SW6_2
from main.src.Controller.SW6_2.SW6_2ControllerObject import SW6_2ControllerObject

# SW5_2
from main.src.Controller.SW5_2.SW5_2CustomerObjectController import SW5_2CustomerObjectController
from main.src.Controller.SW5_2.SW5_2OrderObjectController import SW5_2OrderObjectController

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
# SW6_2ObjectEntity().delete_all_categories()
# SW6_2ControllerObject().bulk_upload()

# Atti Zeugs

# from main.src.Shopware6Bridge.process import *

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
erp_obj = ERPConnectionEntity()
erp_obj.connect()

from main.src.Shopware6Bridge.process import *
while True:
    # Bridge2ObjectTaxController(erp_obj=erp_obj).sync_changed()

    Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_changed()
    sw6_cat.sync_changed_CATEGORIES_from_BRIDGE_to_SW6()

    Bridge2ObjectProductController(erp_obj=erp_obj).sync_changed()
    sw6_prod.sync_changed_PRODUCTS_from_BRIDGE_to_SW6()



# ERPCustomerController(erp_obj=erp_obj_test).sync_changed()
    if BridgeSynchronizeEntity().get_entity_by_id_1().loop_continue == 0:
        break

erp_obj.close()

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


# SW5_2OrderObjectController().get_todays_open_orders()
# SW5_2CustomerObjectController().delete_duplicates_by_adrnr(44760)

# 1. Neuen Bestellungen
# orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(date(year=2023, month=5, day=9))
# for order in orders["data"]:
#     #pprint(order)
#     customer = SW5_2CustomerObjectEntity().get_customer(order["customerId"])
#     # pprint(customer)
#     SW5_2CustomerObjectController().get_new_customer(customer)
#     order_details = SW5_2OrderObjectEntity().get_order_by_id(order["id"])
#     order_data = SW5_2OrderObjectController().get_orders(order_details)
#     #pprint(order)
#     #pprint(order_data)
#     SW5_2OrderObjectController().insert_order_data(order_data)


def get_orders():
    erp_obj = ERPConnectionEntity(mandant="58")
    erp_obj.connect()

    yesterday = datetime.today() - timedelta(days=1)
    orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(startdate=yesterday)
    for order in orders["data"]:
        customer = SW5_2CustomerObjectEntity().get_customer(order["customerId"])
        # Atti
        SW5_2CustomerObjectController().get_new_customer(customer)
        # Flo
        # SW5_2CustomerObjectController().sync_customer(customer=customer["data"])
        customer_double = SW5_2CustomerObjectEntity().get_all_customers_by_adrnr(adrnr=customer["data"]["number"])
        if customer_double["total"] > 1:
            print("Kein Sync! Doppelter Kunde:")
            # SW5_2CustomerObjectController().delete_duplicates_by_adrnr(adrnr=customer["data"]["number"])
        else:
            print("Super, alles ok")
            ERPCustomerController(erp_obj=erp_obj).sync_ranged(start=customer["data"]["number"],end=customer["data"]["number"])

            # Write back the new customer_number
            print("Forward Customer Number", customer["data"]["id"])
            bridge_customer = BridgeCustomerEntity().query.filter_by(api_id=customer["data"]["id"]).one_or_none()

            sw5_customer = SW5_2CustomerObjectEntity()
            # number_added = sw5_customer.set_customer_number_by_id(customer_id=bridge_customer.api_id, number=bridge_customer.erp_nr)
            # print(number_added)

        order_details = SW5_2OrderObjectEntity().get_order_by_id(order["id"])
        order_data = SW5_2OrderObjectController().get_orders(order_details)
        SW5_2OrderObjectController().insert_order_data(order_data)

    # Vorgänge
    bestellungen = ERPOrderController(erp_obj=erp_obj)
    bestellungen.get_new_orders()
    bestellungen.create_new_orders_in_erp()

    # ERP Close'
    erp_obj.close()


def main():
    erp_obj = ERPConnectionEntity(mandant="58")
    erp_obj.connect()

    # ATTI #

    ############# INIT ALL TAXES ##############
    # sw6_tax.init_all_TAXES_from_BRIDGE_to_SW6()

    ############# INIT ALL MEDIAS ##############
    # sw6_media.init_all_MEDIAS_from_BRIDGE_to_SW6()

    ############# INIT ALL CATEG ###############
    # sw6_cat.init_all_CATEGORIES_from_BRIDGE_to_SW6()

    ############# INIT ALL PROD ################
    # sw6_prod.init_all_PRODUCTS_from_BRIDGE_to_SW6()
    # sw6_prod.sync_selected_PRODUCTS_from_BRIDGE_to_SW6(start="7510", end="7510")
    ############# CUSTOMERS ###################
    # sw6_cus.sync_changed_CUSTOMERS_from_BRIDGE_to_SW6()
    # sw6_cus.sync_changed_CUSTOMERS_from_SW6_to_BRIDGE()
    # sw6_cus.upload_new_customers_from_SW6_to_BRIDGE()
    # sw6_cus.sync_all_CUSTOMERS_from_BRIDGE_to_SW6()
    # sw6_cus.sync_selected_CUSTOMERS_from_BRIDGE_to_SW6_without_syncronise_check("e6eb7732af184d9f971832065bc21567", "e6eb7732af184d9f971832065bc21567")

    ############ ORDER FROM SW6 TO BRIDGE ######
    # sw6_order.upload_all_new_orders_from_SW6_to_BRIDGE()
    # order = BridgeOrderEntity.query.get(2)
    # print(order.products[0].get_unit_price(order))

    ############ ORDER FROM SW5 TO BRIDGE ######
    # orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate_and_enddate(
    #     startdate=date(year=2023, month=4, day=19),
    #     enddate=date(year=2023, month=4, day=20),
    # )
    # orders = SW5_2OrderObjectEntity().get_todays_open_orders()

    yesterday = datetime.today() - timedelta(days=4)
    orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(startdate=yesterday)
    for order in orders["data"]:
        customer = SW5_2CustomerObjectEntity().get_customer(order["customerId"])
        # Atti
        SW5_2CustomerObjectController().get_new_customer(customer)
        # Flo
        # SW5_2CustomerObjectController().sync_customer(customer=customer["data"])
        customer_double = SW5_2CustomerObjectEntity().get_all_customers_by_adrnr(adrnr=customer["data"]["number"])
        if customer_double["total"] > 1:
            print("Kein Sync! Doppelter Kunde:")
            # SW5_2CustomerObjectController().delete_duplicates_by_adrnr(adrnr=customer["data"]["number"])
        else:
            print("Super, alles ok")
            ERPCustomerController(erp_obj=erp_obj).sync_ranged(start=customer["data"]["number"],end=customer["data"]["number"])

            # Write back the new customer_number
            print("Forward Customer Number", customer["data"]["id"])
            bridge_customer = BridgeCustomerEntity().query.filter_by(api_id=customer["data"]["id"]).one_or_none()

            sw5_customer = SW5_2CustomerObjectEntity()
            # number_added = sw5_customer.set_customer_number_by_id(customer_id=bridge_customer.api_id, number=bridge_customer.erp_nr)
            # print(number_added)

        order_details = SW5_2OrderObjectEntity().get_order_by_id(order["id"])
        order_data = SW5_2OrderObjectController().get_orders(order_details)
        SW5_2OrderObjectController().insert_order_data(order_data)


    """
    ######################
    Syncing
    ######################
    """

    # Tax
    # Bridge2ObjectTaxController(erp_obj=erp_obj).sync_all()  # OK!
    # sync_all_tax()

    # Categories
    # Bridge2ObjectCategoryController(erp_obj=erp_obj).sync_all()  # OK!
    # sync_all_categories()
    # sync_all_changed_categories()

    # Products
    # Bridge2ObjectProductController(erp_obj=erp_obj).sync_changed()  #  sync_all_changed_products()
    # Bridge2ObjectProductController(erp_obj=erp_obj).sync_all()

    # Adressen
    # ERPCustomerController(erp_obj=erp_obj).sync_changed()

    # Vorgänge
    bestellungen = ERPOrderController(erp_obj=erp_obj)
    bestellungen.get_new_orders()
    bestellungen.create_new_orders_in_erp()

    # History
    # erp_history = ERPHistoryEntity(erp_obj=erp_obj)

    # sync_all_addresses()
    # os.system("shutdown /s /t 1")

    # All
    # sync_all_to_db()

    erp_obj.close()

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

    @app.route('/customer/compare/<adrnr>')
    def show_customers_to_compare(adrnr: str):
        sw_customer_raw = SW5_2CustomerObjectEntity().get_customer(customer_id=adrnr, is_number_not_id=True)
        sw_customer = BridgeCustomerEntity().map_sw5_to_db(sw_customer_raw["data"])

        

        return render_template(
            'classei/customer/customer_compare.html',
            sw_customer=sw_customer,
            adrnr=adrnr)


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

    @app.route('/<domain>/email/<year>/<newsletter>/<erp_nums>')
    def render_and_save_mjml(domain, year, newsletter, erp_nums):
        # Set Project path
        project_path = os.path.abspath("D:/htdocs/python/GC-Bridge/main")
        # Set the path
        path = os.path.abspath(os.path.join(project_path, 'templates', domain, 'email', year, newsletter))

        # Make sure, the directory exists. If not, create it
        os.makedirs(path, exist_ok=True)

        # Get the erp_nums as list
        erp_nums_str = erp_nums.split(',')
        erp_nums_list = list(map(str, erp_nums_str))

        # Get the products in the correct order
        products = []
        for erp_num in erp_nums_list:
            print(erp_num)
            product = BridgeProductEntity.query.filter_by(erp_nr=erp_num).one_or_none()
            if product:
                products.append(product)

        special_end_date = False
        for product in products:
            # This is for the product url
            for category in product.categories:
                parent_category = BridgeCategoryEntity.query.filter_by(api_id=category.api_idparent).one()
                category.parent_category = parent_category

            images = []
            # This is for the images
            for image in product.image:
                image_str = json.dumps(image)
                images.append(json.loads(image_str))
            product.images = images

            # This is for the disclaimer
            if product.get_special_price():
                special_end_date = product.prices.special_end_date

        # Get the html content
        rendered_html = render_template(f"/{domain}/email/{year}/{newsletter}/newsletter.mjml", products=products,
                                        special_end_date=special_end_date)

        # Schreiben Sie den Inhalt des Newsletters in eine HTML-Datei
        rendered_mjml_file = os.path.join(path, f"{newsletter}.mjml")
        with open(rendered_mjml_file, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        npm_path = f"main/templates/{domain}/email/{year}/{newsletter}/{newsletter}"
        npm_mjml_path = npm_path + ".mjml"
        npm_html_path = npm_path + ".html"
        npm_text_path = npm_path + ".text"

        with open(npm_text_path, "w", encoding="utf-8") as f:
            text_content = html2text.html2text(rendered_html)
            f.write(text_content)

        print("mjml -w", rendered_mjml_file, "-o", npm_html_path)

        return render_template(f'/classei/email/{year}/{newsletter}/{newsletter}.html')


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

    # app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
