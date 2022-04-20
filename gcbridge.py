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
from main.src.Entity.Bridge.Tax.BridgeTaxEntity import *
from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *

from main.src.Controller.Mappei.parser import *
from main.src.Controller.ERP.ERPController import *
import pymysql

"""
######################
Tests
#######################
"""
from main.src.Controller.SW6.SW6CategoryController import *
from main.src.Entity.Mappei.MappeiProductEntity import *
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
    # erp_connect()
    sync_all_products()
    # erp_close()

    """
    ######################
    Tests
    ######################
    """
    # tests()
    # EOF main

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
    # @app.route('/')
    # def index():
    #     content = "Some filling Text from gcbridge.py"
    #     # Forward var "content" to the template to read it in the template like {{content}}
    #     return render_template('index.html', content=content)
    #
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
    # product = erp_get_dataset("Artikel")
    # mappe = erp_get_dataset_by_id(product, "Nr", "204116")
    # product_dataset = Bridge
    # product_dataset.dataset_save_to_db(mappe)



    # mandant = erp_get_dataset('Mandant')
    # steuern = mandant.NestedDataSets("Ust")
    # steuern_count = erp_get_dataset_record_count(steuern)
    # print("Es gibt %s Steuersätze im Mandanten %s" % (steuern_count, mandant.Fields.Item('MandNr').AsString))
    # i = 0
    # while i < steuern_count:
    #     print("(%s) %s: %s" % (steuern.Fields.Item("StSchl").AsInteger,steuern.Fields.Item("Bez").AsString, steuern.Fields.Item("Sz").AsFloat))
    #     steuern.Next()
    #     i += 1
    #
    # erp_close()




""" 
######################
Server
######################
"""
print(__name__)
# check if we are in the main Script? Thread? Check for __main__
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        main()
    # Run in debug mode and
    # do not restart the server
    #
    # app.run(debug=True, use_reloader=True)
