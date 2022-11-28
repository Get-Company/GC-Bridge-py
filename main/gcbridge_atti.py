from flask_migrate import Migrate
from main.src.Controller.Bridge2.Bridge2ObjectOrderController import Bridge2ObjectOrderController
from main import create_app
from main.src.Entity.Mappei.MappeiProductEntity import *
from main.src.Controller.SW6.SW6InitController import SW6InitController
from main.src.Controller.SW6.SW6UpdatingController import SW6UpdatingController
from main.src.Entity.Bridge.Orders.BridgeOrderEntity import *
from pprint import pprint
app = create_app()
app.app_context().push()
#
# migrate = Migrate(app, db)
#
def main():
    SW6InitController().init_all()
    # get_orders_from_sw6 = Bridge2ObjectOrderController().get_orders_product()
    # pprint(get_orders_from_sw6)






# check if we are in the main Script? Thread? Check for __main__
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        main()
    # Run in debug mode and
    # do not restart the server
    #
    # app.run(debug=True, use_reloader=True)
