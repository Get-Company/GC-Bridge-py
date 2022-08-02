from main import create_app
import sys
from flask import render_template, request
from flask_migrate import Migrate
from main.src.Controller.Bridge.BridgeController import *

"""
######################
Models
######################
"""
# Entities
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import *
from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *
# Mappei
from main.src.Entity.Mappei.MappeiProductEntity import MappeiProductEntity
from main.src.Entity.Mappei.MappeiPriceEntity import MappeiPriceEntity
# Controller
from main.src.Controller.Mappei.parser import *
from main.src.Controller.ERP.ERPController import *
from main.src.Controller.ERP.ERPObjectController import *
from main.src.Controller.SW5.SW5DuplicateAddressController import *

import pymysql

"""
######################
Tests
#######################
"""
import PySimpleGUI as sg
from main.src.Controller.SW6.SW6CategoryController import *
from main.src.Controller.SW5.SW5AddressController import *
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity
from main.src.Entity.ERP.ERPArtkelEntity import *
from main.src.Entity.ERP.ERPArtikelKategorieEntity import *
from main.src.Entity.ERP.ERPAdressenEntity import *
from main.src.Entity.ERP.ERPVorgangEntity import *

# Flask and ERP Test
import win32com.client as win32
import pythoncom

import re
import os

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


def main():
    """
    ######################
    ERP
    ######################
    """
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
    sync_all_addresses()
    # os.system("shutdown /s /t 1")

    # All
    # continuously
    # erp_connect()
    # while True:
    #     sync_all_continuously(False)
    # erp_close()

    # sync_all_to_db()

    """
    ######################
    Tests
    ######################
    """
    # tests()
    # EOF main


    """
    ######################
    SW5
    ######################
    Get duplicates in Sync. All Adresses from "False" are synced to "Right"
    """
    # sw5_sync_duplicates_v2(false_adrnr=12681, right_adrnr=29624)

    # @app.route('/customer/duplicate_customers/<false_adrnr>/<right_adrnr>')
    # def duplicate_customers(false_adrnr, right_adrnr):
    #     pythoncom.CoInitialize()
    #     erp = win32.dynamic.Dispatch('BpNT.Application')
    #     erp.Init('Egon Heimann GmbH', "", 'f.buchner', '')
    #     erp.SelectMand('58')
    #     dataset_info = erp.DataSetInfos.Item("Artikel")
    #     dataset = dataset_info.CreateDataSet()
    #     dataset.FindKey("Nr", "204116")
    #     erp_mappe = dataset
    #     return render_template('customer/duplicate_customers.html', name=erp_mappe.Fields.Item('ArtNr').AsString)

    # sg.theme("Dark")
    # layout = [
    #     [sg.Text('Try ERP', size=(15,1))],
    #     [sg.Button('Connect ERP', key='connect')],
    #     [sg.Text("Delete Customer from SW5")],
    #     [sg.Button("Delete", key='customer.delete')]
    # ]
    # window = sg.Window("ERP-Test", layout)
    # while True:
    #     event, values = window.read()
    #     # End Programm if user closes window or presses a brutto
    #     if event == sg.WIN_CLOSED:
    #         erp_obj.close()
    #         break
    #     if event == 'connect':
    #         erp_obj = ERPObjectController(mandant='58')
    #     if event == 'customer.delete':
    #         erp_connect('58')
    #         sw5_delete_customer(51828)
    #         erp_close()
    #
    # window.close()

    """
    ######################
    Mappei
    ######################
    When activated it asks you in the CLI if you want to download and save the xml,
    then reads the xml with parse and xmlreader and saves all information in the db
    """
    # This is just a CLI Version which watches for inout
    # get_products_list()
    """
    ######################
    Flask Server
    ######################
    """

    # Standard Route for index
    # @app.route('/product/<erp_nr>')
    # def index(erp_nr):
    #     Products = BridgeProductEntity()
    #     product = Products.query.filter_by(erp_nr=erp_nr).first()
    #
    #     # Forward var "content" to the template to read it in the template like {{content}}
    #     return render_template('product.html', product=product)
    #
    # Offer compare to Mappei
    # @app.route('/offer', methods=['POST', 'GET'])
    # def offer():
    #     erp_nrs = request.form.getlist('erp[]')
    #     amounts = request.form.getlist('amount[]')
    #     Products = BridgeProductEntity
    #     products = []
    #
    #     for erp_nr, amount in zip(erp_nrs, amounts):
    #         print("ErpNr: %s, Amount: %s" % (erp_nr, amount))
    #         product = Products.query.filter_by(erp_nr=erp_nr).first()
    #         product.amount = amount
    #         product.sum = product.get_price(amount)
    #         products.append(product)
    #
    #     return render_template('offer.html', products=products)

    # @app.route('/mappei/match')
    # def mappei_match():
    #     products = BridgeProductEntity.query.order_by(BridgeProductEntity.erp_nr.asc()).limit(10).all()
    #     m_products = MappeiProductEntity.query.order_by(MappeiProductEntity.nr.asc()).all()
    #     return render_template('mappei/match.html', products=products)

    # @app.route('/mappei/match/ajax/get_mappei_product', methods=['GET', 'POST'])
    # def get_mappei_product_ajax():
    #     if request.method == 'POST':
    #         search = "%{}%".format(request.form['data'])
    #         m_products = MappeiProductEntity.query.filter(MappeiProductEntity.nr.like(search)).asc().all
    #         return m_products

    # cat_api = SW6CategoryController()
    # cat_api.db_save_all_to_sw6()
    # cat_ntt = BridgeCategoryEntity.query.filter_by(erp_nr=110).first()
    # cat_api.upsert_ntt(cat_ntt)

    # prod_api = SW6ProductController()
    # prod_api.db_save_all_to_sw6()
    # prod_ntt = BridgeProductEntity.query.filter_by(erp_nr=204013).first()
    # print("gcbridge - %s" % prod_ntt.name)
    # prod_api.upsert_ntt(prod_ntt, add_parent=False)
    # prod_api.upsert_images_to_sw6(prod_ntt)
    # prod_ntt = BridgeProductEntity.query.filter_by(erp_nr=204113).first()
    # prod_api.upsert_images_to_sw6(prod_ntt)

    # mappe_classei = BridgeProductEntity.query.filter_by(erp_nr='204116').first()
    # print("Der passende Mappei Artikel dazu ist: %s" % mappe_classei.mappei[0].nr)
    # tax = BridgeTaxEntity.query.filter_by(steuer_schluessel=20).first()
    # print("%s bekommt %s Steuer." % (mappe_classei.name, tax.description))
    # mappe_classei.tax = tax
    # db.session.add(mappe_classei)
    # db.session.commit()

    # erp_connect()
    # erp_product = erp_get_dataset("Artikel")
    # erp_mappe = erp_get_dataset_by_id(erp_product, "Nr", "204116")
    # ntt_product = Product()
    # ntt_product.dataset_save_to_db(erp_mappe)
    # erp_close()


""" 
######################
Server
######################
"""
# check if we are in the main Script? Thread? Check for __main__
if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        main()
    # Run in debug mode and
    # do not restart the server
    # localhost:5000
    # app.run(port=5000, debug=True, use_reloader=True)
