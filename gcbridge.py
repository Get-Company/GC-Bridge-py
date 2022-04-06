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
from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from main.src.Entity.Bridge.Category.BridgeCategoryEntity import *
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *
from main.src.Controller.Mappei.parser import *
import pymysql

"""
######################
Tests
#######################
"""
from main.src.Controller.SW6.SW6CategoryController import *
from main.src.Controller.SW6.SW6ProductController import *

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

    # Products
    # sync_all_changed_products()
    # sync_all_products()

    # Adressen
    # sync_all_addresses()

    # All
    # erp_connect()
    # try:
    #     while True:
    #         sync_all_continuously()
    # except KeyboardInterrupt:
    #     erp_close()
    #     pass
    # except StopIteration:
    #     print("Iteration Stop")

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

    # get_products_list()

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
    #
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

    prod_api = SW6ProductController()
    prod_api.db_save_all_to_sw6()
    # prod_ntt = BridgeProductEntity.query.filter_by(erp_nr=204013).first()
    # print("gcbridge - %s" % prod_ntt.name)
    # prod_api.upsert_ntt(prod_ntt, add_parent=False)
    # prod_api.upsert_images_to_sw6(prod_ntt)
    # prod_ntt = BridgeProductEntity.query.filter_by(erp_nr=204113).first()
    # prod_api.upsert_images_to_sw6(prod_ntt)


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
