from main import create_app
from main.src.Entity.Mappei.MappeiProductEntity import *
from main.src.Controller.SW6.SW6InitController import SW6InitController
from main.src.Controller.SW6.SW6UpdatingController import SW6UpdatingController


"""
Hallo Flori!
"""
# app = create_app()
# app.app_context().push()

# migrate = Migrate(app, db)


SW6InitController().init_all()
#SW6UpdatingController().sync_changed_to_sw()



# # check if we are in the main Script? Thread? Check for __main__
# if __name__ == "__main__":
#     with app.app_context():
#         #db.create_all()
#         main()
#     # Run in debug mode and
#     # do not restart the server
#     #
#     # app.run(debug=True, use_reloader=True)
