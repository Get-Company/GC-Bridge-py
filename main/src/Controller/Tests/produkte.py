
def test1():
    """
    Find Produkt 584470 in ERP and db
    Print its categories
    Map the erp to DB
    commit it to db
    :return:
    """
    db = "Import db from main"
    erp_obj = 'Import erp_obj from  Entity and make connection'
    ERPArtikelEntity = 'Import ERPArtikelEntity from Entity'
    BridgeProductEntity = 'Import BridgeProductEntity from Entity'

    prod_erp = ERPArtikelEntity(erp_obj=erp_obj, id_value='584470')
    prod_in_db = BridgeProductEntity().query.filter_by(erp_nr=584470).first()
    print(prod_in_db.categories)
    prod_to_db = BridgeProductEntity().map_erp_to_db(prod_erp)
    db.session.add(prod_to_db)
    db.session.commit()