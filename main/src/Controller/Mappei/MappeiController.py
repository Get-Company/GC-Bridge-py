from main.src.Entity.Bridge.Product.BridgeProductEntity import *
from main import db


# Get the prices with the parser from xmlreader
# get_products_list(db, app)

def set_classei_mappei_relation(classei_nr, mappei_nr, ):

    classei = BridgeProductEntity.query.filter_by(erp_nr=classei_nr).first()
    if not classei:
        return
    mappei = MappeiProductEntity.query.filter_by(nr=mappei_nr).first()
    if not mappei:
        return
    if mappei in classei.mappei:
        print('Found "%s(%s)" is already bound to "%s(%s)"' % (mappei.name, mappei.id, classei.name, classei.id))
        classei.mappei.remove(mappei)
        return

    print("Set relation between", classei_nr, 'and', mappei_nr)

    classei.mappei.append(mappei)
    db.session.add(classei)
    db.session.commit()
