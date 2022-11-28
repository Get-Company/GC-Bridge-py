from main.src.Entity.SW6.SW6InitEntity import SW6InitEntity
#from main.src.Entity.SW6.SW6MediaInitEntity import SW6MediaInitEntity


class SW6InitController:
    def init_all(self):

        # entity = SW6InitEntity("category")
        # entity.init_entity()

        # entity = SW6InitEntity("category_with_parent")
        # entity.init_entity()
        #
        entity = SW6InitEntity("product")
        entity.init_entity()
        #
        # entity = SW6MediaInitEntity("media")
        # entity.init_entity()

        # for parameter in ["products"]:
        #      controller = SW6InitEntity(parameter)
        #      controller.init_entity()



