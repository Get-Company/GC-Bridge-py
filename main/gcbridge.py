import os
from io import StringIO
from pprint import pprint
000
import html2text
import subprocess
import sqlalchemy
from datetime import datetime, timedelta

from main import create_app
from flask import render_template, redirect, request, make_response, jsonify
from flask_migrate import Migrate

import sys
from sqlalchemy import and_, or_
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
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity
from main.src.Entity.SW5_2.SW5_2AddressObjectEntity import SW5_2AddressObjectEntity
from main.src.Entity.SW5_2.SW5_2ProductObjectEntity import SW5_2ProductObjectEntity
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity
from main.src.Entity.SW5_2.SW5_2MiscObjectEntity import SW5_2MiscObjectEntity

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



# erp_obj = ERPConnectionEntity(mandant="58")
# erp_obj.connect()
# Bridge2ObjectProductController(erp_obj=erp_obj).sync_range('204045', '204045/06')
# erp_obj.close()
# customer = ERPAnschriftenEntity(erp_obj=erp_obj)
# # for index in customer.created_dataset.Indices:
# #     for index_field in index.IndexFields:
# #         print(index.Name, " - ", index_field.Name)
# customer.set_range_wildcard("Na2", '?Mösch')
# customer.filter_expression('Ort = "Offenbach"')
# customer.range_first()
# while not customer.range_eof():
#     print(customer.get_("AdrNr"))
#     customer.range_next()
#
# ds_customer = erp_obj.get_erp().DataSetInfos("Anschriften").CreateDataSetEx()
# ds_customer.Indices("Na2").Select()
# ds_customer.WildcardRange('?Möschle')
# ds_customer.First()
# print(f"'?Möschle' found {ds_customer.RecordCount}x")
# while not ds_customer.EOF:
#     print(ds_customer.Fields("AdrNr").AsString)
#     ds_customer.Next()

# erp_obj.close()

def main():
    # erp_obj = ERPConnectionEntity(mandant="58")
    # erp_obj.connect()

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
    # Bridge2ObjectProductController(erp_obj=erp_obj).sync_range('204045/00', '204046')

    # Bridge2ObjectProductController(erp_obj=erp_obj).sync_all()

    # Adressen
    # ERPCustomerController(erp_obj=erp_obj).sync_changed()

    # Vorgänge
    # bestellungen = ERPOrderController(erp_obj=erp_obj)
    # bestellungen.get_new_orders()
    # bestellungen.create_new_orders_in_erp()

    # History
    # erp_history = ERPHistoryEntity(erp_obj=erp_obj)

    # sync_all_addresses()
    # os.system("shutdown /s /t 1")

    # All
    # sync_all_to_db()

    # erp_obj.close()


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

    @app.route("/gc-bridge/orders")
    def gcbridge_orders():
        yesterday = datetime.today() - timedelta(days=1)
        sw5_orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(startdate=yesterday)

        return render_template(("/classei/orders/orders.html"), orders=sw5_orders)

    @app.route("/gc-bridge/erp/adresse/<adrnr>/_action")
    def gcbridge_erp_adresse_action(adrnr):
        erp_obj = ERPConnectionEntity(mandant="58")
        erp_obj.connect()
        try:
            erp_customer = ERPAdressenEntity(erp_obj=erp_obj, id_value=int(adrnr))
            response = erp_customer.get_address_json()
        except:
            response["message"] = f"Adresse {adrnr} nicht gefunden"
        erp_obj.close()
        return jsonify(response)

    @app.route("/gc-bridge/sw5/customer/address/<address_id>/_action")
    def gcbridge_sw5_customer_address_action(address_id):
        try:
            response = SW5_2CustomerObjectEntity().get_customer_address_by_id(address_id=address_id)
        except:
            response["message"] = f"Adresse {address_id} in SW5 nicht gefunden"

        return response

    @app.route("/gc-bridge/order/<order_id>")
    def gcbridge_order(order_id):
        sw5_order = SW5_2OrderObjectEntity().get_order_by_id(order_id)
        sw5_customer = SW5_2CustomerObjectEntity().get_customer(sw5_order["data"]["customer"]["id"])

        sw5_addresses = []
        for address in sw5_customer["data"]["addresses"]:
            current_address = SW5_2AddressObjectEntity().get_address(address['id'])
            sw5_addresses.append(current_address)

        sw5_countries = SW5_2MiscObjectEntity().get_countires()

        return render_template("/classei/orders/order.html",
                               sw_order=sw5_order,
                               sw_customer=sw5_customer,
                               sw_addresses=sw5_addresses,
                               sw_countries=sw5_countries,
                               )

    @app.route("/gcbridge/erp/adresse/alternative_adrnrs/_action", methods=['POST'])
    def gcbridge_erp_adresse_alternative_adrnrs_action():
        adrnr = request.form.get('adrnr')
        company = request.form.get("company")
        na2 = request.form.get('na2')
        street = request.form.get('street')
        plz = request.form.get('plz')

        erp_obj = ERPConnectionEntity(mandant="58")
        erp_obj.connect()
        response = {
            "data": []
        }

        adressen_street = ERPAnschriftenEntity(erp_obj=erp_obj)
        # adressen_na2 = ERPAnschriftenEntity(erp_obj=erp_obj)
        try:
            adressen_street.filter_expression(f"Str='{street}' and PLZ='{plz}'")
            print("Suche nach doppelter Adresse in Str", street, "und PLZ", plz)
            adressen_street.filter_set()
            while not adressen_street.range_eof():
                address_fields = adressen_street.get_special_standard_address_fields()
                response["data"].append(address_fields)
                adressen_street.range_next()
        except:
            response["message"] = "Error on searching alternative adrnrs"
        erp_obj.close()
        return jsonify(response)

    @app.route("/erp/search_address_by/<field>/and/<value>/_action")
    def erp_search_by_field_value(field, value):
        response = {
            'status': 'success',
            'message': "",
            'data': {}
        }

        erp_obj = ERPConnectionEntity()
        erp_obj.connect()
        address = ERPAdressenEntity(erp_obj=erp_obj)
        found = address.find_(field=field, value=value)

        if found:
            response["status"] = "Success"
            adrnr = address.get_('AdrNr')
            print(adrnr)
            response["message"] = f"AdrNr: {adrnr}"

        erp_obj.close()
        return jsonify(response)

    """ 
    E-Mail 
    """

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

    """ 
    Order Functions and urls 
    """

    @app.route("/gc-bridge/get-orders")
    def gcbridge_get_orders():
        # Check the date
        start_date_arg = request.args.get('start_date')
        if start_date_arg and start_date_arg.strip():
            try:
                start_date = datetime.strptime(start_date_arg, "%Y-%m-%dT%H:%M")
            except ValueError:
                start_date = datetime.now()
        else:
            start_date = datetime.now()
        yesterday = (start_date - timedelta(days=1)).replace(hour=0, minute=0)

        # Get the states
        order_state = request.args.get('order_state') or None
        payment_state = request.args.get('payment_state') or None

        print("Order State", order_state)

        # Start the query build
        query = BridgeOrderEntity.query

        # Add the Date
        query = query.filter(BridgeOrderEntity.purchase_date >= start_date)

        if order_state:
            query = query.filter(BridgeOrderEntity.order_state.has(order_state=order_state))

        if payment_state:
            query = query.filter(BridgeOrderEntity.order_state.has(payment_state=payment_state))

        orders = query.all()

        for order in orders:
            order.add_order_product_fields_to_product()

        return render_template("classei/orders/get-orders_v2.html",
                               start_date=start_date,
                               order_state=order_state,
                               payment_state=payment_state,
                               orders=orders,
                               yesterday=yesterday)

    @app.route("/gcbridge/get-orders/<startdate>/_action")
    def gcbridge_get_orders_from_startdate(startdate):
        startdate = datetime.strptime(startdate, "%Y-%m-%dT%H:%M")
        response = {
            'status': 'success',
            'message': "",
            'data': {},
            'success': True  # Setzen Sie success auf True
        }
        orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(startdate=startdate)

        if orders['success']:
            response['message'] = f"{orders['total']} offene Bestellungen seit {startdate.strftime('%d.%m.%Y')} gefunden"

            for order in orders["data"]:
                customer = SW5_2CustomerObjectEntity().get_customer(customer_id=order["customer"]["id"])

                if customer["success"]:
                    bridge_customer = SW5_2CustomerObjectController().upsert_customer(customer)

                    if bridge_customer is None:
                        response["status"] = "Customer Error. No Email or Number"
                        response["message"] = \
                            f"E-Mail:{customer['data']['email']} " \
                            f"or Number: {customer['data']['number']}" \
                            "is missing."
                        response['success'] = False  # Setzen Sie success auf False, wenn ein Fehler aufgetreten ist
                    if not bridge_customer:
                        response["status"] = "Customer Error"
                        response["message"] = f"Something went wrong with customer {customer['data']['id']}"
                        response['success'] = False  # Setzen Sie success auf False, wenn ein Fehler aufgetreten ist

                bridge_order = SW5_2OrderObjectController().upsert_order(order)

                if bridge_order is None:
                    response["status"] = "Order Error. No Order Details Found"
                    response["message"] += f"Error on Order id. {order['id']}"
                    response['success'] = False  # Setzen Sie success auf False, wenn ein Fehler aufgetreten ist

        return jsonify(response), 200

    @app.route('/update_erp_nr/', methods=['POST'])
    def update_erp_nr():
        customer_id = request.form.get('customerId')
        new_erp_nr = request.form.get('newErpNr')
        try:
            # update the customer
            customer = BridgeCustomerEntity.query.get(customer_id)
            customer.erp_nr = new_erp_nr

            # update the addresses
            addresses = customer.addresses
            for address in addresses:
                address.erp_nr = new_erp_nr

            db.session.commit()

            return jsonify({"status": "success", "message": "ERP Nr updated successfully."})

        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to update ERP Nr: {e}"})

    @app.route("/gcbridge/create_order/<customer_id>/<order_id>/_action")
    def gcbridge_create_order_customer_id_order_id(customer_id, order_id):
        response = {
            'status': 'success',
            'message': "",
            'data': {}
        }
        try:
            bridge_customer = BridgeCustomerEntity.query.get(customer_id)
            response["status"] = 'success'
            response["message"] += "Customer found in db "
        except Exception as e:
            response["status"] = 'error'
            response["message"] += f"Customer not found in db by id: {customer_id}: {e} "
            return jsonify(response)

        try:
            bridge_order = BridgeOrderEntity.query.get(order_id)
            response["status"] = 'success'
            response["message"] += "Order found in db "
        except Exception as e:
            response["status"] = 'error'
            response["message"] += f"Order not found in db by id: {order_id}: {e} "

        # Sync Customer to ERP
        erp_obj = ERPConnectionEntity()
        erp_obj.connect()
        try:
            result = ERPCustomerController(erp_obj=erp_obj).sync_bridge_customer_to_erp(bridge_customer)

            if result is True:
                response["status"] = 'success'
                response["message"] += "New Customer in ERP created.\n"
            elif result is False:
                response["status"] = 'error'
                response["message"] += "New Customer was not created!\n"
            else: # an 'AdrNr' was returned
                response["status"] = 'success'
                response["message"] += f"Customer successfully synced with ERP. AdrNr is {result}.\n"

        except Exception as e:
            response["status"] = 'error'
            response["message"] += f"An error occurred during the process: {e}\n"

        # Sync Bestellung to ERP
        bestellungen = ERPOrderController(erp_obj=erp_obj)
        bestellungen.create_new_order_in_erp(bridge_order)

        erp_obj.close()
        return jsonify(response)

    @app.route("/gcbridge/set_states/<order_id>/<payment_status_id>/<order_status_id>")
    def gcbridge_set_states(order_id, payment_status_id, order_status_id):
        # Prüfen ob alle Parameter vergeben sind
        response = {}
        if not order_id or not payment_status_id or not order_status_id:
            response["status"] = "error"
            response["message"] = "Missing parameters. All parameters (order_id, payment_status_id, order_status_id) are required."
            return jsonify(response), 400

        order_entity = BridgeOrderEntity()
        order = order_entity.query.get(order_id)

        if not order:
            response["status"] = "error"
            response["message"] = f"No order found with id: {order_id}"
            return jsonify(response), 404

        order.order_state.payment_state = payment_status_id
        order.order_state.shipping_state = 0
        order.order_state.order_state = order_status_id

        try:
            sw5_status = SW5_2OrderObjectEntity().set_order_and_payment_status(
                order_id=order.api_id,
                payment_status_id=payment_status_id,
                order_status_id=order_status_id
            )

            print("SW5 States Response:", sw5_status)

            if not sw5_status:
                response["status"] = "error"
                response["message"] = f"Failed to set order and payment status in SW5 for order_id: {order_id} and payment_id: {payment_status_id}"
                return jsonify(response), 500

            db.session.add(order)
            db.session.commit()
            db.session.close()

            response["status"] = "success"
            response["message"] = "Order and payment status updated successfully."
            return jsonify(response), 200

        except Exception as e:
            db.session.rollback()
            response["status"] = "error"
            response["message"] = f"Updating States in SW5 gone wrong with order_id: {order_id} and payment_id: {payment_status_id}. Error: {e}"
            return jsonify(response), 500

    @app.route("/gcbridge/check_sw5_orders_against_db_orders/<startdate>/_action")
    def gcbridge_check_sw5_orders_against_db_orders():
        sw5_orders = SW5_2OrderObjectEntity.get_open_orders_by_startdate()
        pass


    """ 
    Customer functions 
    """
    @app.route("/customer/is_duplicate/<erp_nrs>")
    def gcbridge_customer_is_duplicate(erp_nrs):
        # Get the erp_nums as list
        erp_nums_str = erp_nrs.split(',')
        erp_nums_list = list(map(int, erp_nums_str))

        sw5_customers = []
        for erp_nr in erp_nums_list:
            response = SW5_2CustomerObjectEntity().get_all_customers_by_adrnr(int(erp_nr))
            if response["success"]:
                sw5_customers.extend(response["data"])

        bridge_customers = BridgeCustomerEntity.query.filter(or_(BridgeCustomerEntity.erp_nr == erp_num for erp_num in erp_nums_list)).all()
        bridge_customer_addresses = BridgeCustomerAddressEntity.query.filter(or_(BridgeCustomerAddressEntity.erp_nr == erp_num for erp_num in erp_nums_list)).all()

        return render_template("classei/customer/customers_duplicates.html",
                               erp_nrs=erp_nums_list,
                               bridge_customers=bridge_customers,
                               bridge_customer_addresses=bridge_customer_addresses,
                               sw5_customers=sw5_customers
                               )

    @app.route("/customer/remove_webshop_id/<erp_nr>/_action")
    def gcbridge_customer_remove_webshop_id(erp_nr):
        response = {
            'status': 'success',
            'message': "",
            'data': {}
        }
        try:
            erp_obj = ERPConnectionEntity()
            erp_obj.connect()
            client = ERPAdressenEntity(id_value=erp_nr)
            webshop_id = client.get_("WShopID")
            client.remove_webshop_id()
            response["status"] = "success"
            response["message"] = f"Webshop ID {webshop_id} was removed from client {erp_nr}"
        except Exception as e:
            print(f"Error on remove webshop id: {webshop_id} from client: {erp_nr}")
            response["status"] = 'error'

    @app.route("/customer/erp/search/_action")
    def gcbridge_customer_erp_search(dataset, field, value):
        response = {
            'status': 'success',
            'message': "",
            'data': {}
        }
        erp_obj = ERPConnectionEntity()
        erp_obj.connect()

        ds_customer = erp_obj.get_erp().DataSetInfos(dataset).CreateDataSetEx()
        ds_customer.Indices(field).Select()
        ds_customer.WildcardRange(value)
        ds_customer.First()

        print(f"{field} = {value} found in {dataset} {ds_customer.RecordCount}x")
        while not ds_customer.EOF:
            print(ds_customer.Fields("AdrNr").AsString)
            ds_customer.Next()

        erp_obj.close()

    @app.route("/customer/bridge/delete/address/<id>/_action")
    def gcbridge_customer_bridge_delete_address(id):
        response = {
            'status': 'success',
            'message': "",
            'data': {}
        }

        try:
            # Start a database transaction
            db.session.begin()

            # Query the database for the customer address
            customer_address_in_db = BridgeCustomerAddressEntity.query.get(id)

            if customer_address_in_db is None:
                # If the customer address doesn't exist, update the response and rollback transaction
                response['status'] = 'fail'
                response['message'] = f'No address found with ID: {id}'
                db.session.rollback()
            else:
                # If the customer address exists, delete it from the database
                db.session.delete(customer_address_in_db)
                db.session.commit()  # Commit transaction if everything went fine

                response['message'] = f'Successfully deleted address with ID: {id}'

        except Exception as e:
            # If something went wrong with the database operation, rollback the transaction and update the response
            db.session.rollback()
            response['status'] = 'fail'
            response['message'] = str(e)

        return jsonify(response)








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

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
