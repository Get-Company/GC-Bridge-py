from main.src.Entity.SW6.SW6InitEntity import SW6InitEntity
from main.src.Entity.SW6.SW6MediaInitEntity import SW6MediaInitEntity


class SW6InitController:
    def init_all(self):

        # entity = SW6MediaInitEntity("media")
        # entity.init_entity()

        # entity = SW6MediaInitEntity("categegory")
        # entity.init_entity()
        #
        # entity = SW6MediaInitEntity("media")
        # entity.init_entity()
        #
        # entity = SW6MediaInitEntity("media")
        # entity.init_entity()

        for parameter in ["product"]:
             controller = SW6InitEntity(parameter)
             controller.init_entity()



