# API
from main.src.Controller.SW6.extended.SubMedia import SubMedia
from main.src.Controller.SW6.extended.SubProduct import SubProduct
# Controller
from main.src.Controller.SW6.SW6ObjectController import SW6ObjectController
from main.src.Controller.SW6.SW6MediaController import SW6MediaController
# Entity
from main.src.Entity.Bridge.Product import BridgeProductEntity

from main.src.Entity.Bridge.Product.BridgeProductEntity import BridgeProductEntity
from main.src.Entity.SW6.Archiv_Entitys.SW6ProductEntity import SW6ProductEntity


class SW6ProductController(SW6ObjectController):
    def __init__(self):
        # Initiate all variables to forward them to super.__init__
        self.entity_name = "product"
        self.entity_check_field = "id"
        self.entity_instance = SW6ProductEntity()
        self.api_sub_instance_media = SubMedia()
        self.api_sub_instance_product = SubProduct()
        self.sw6_media_controller = SW6MediaController()
        self.class_name = "SW6ProductController"

        super().__init__(
            entity_name=self.entity_name,
            entity_instance=self.entity_instance,
            entity_check_field=self.entity_check_field,
            class_name=self.class_name
        )

    def db_save_all_to_sw6(self):
        """
        For the 1. Sync, we need to sync all the categories to sw6, but without the parent.
        When a category is synced with a parent and it doesn't already exist in sw6, we get an error.

        So to sync all properly we need 2 syncs. First all the Categories - then again but with their parent
        :param add_parent:
        :return:
        """
        self.print_method_info(self.class_name)
        # 1. Sync without parent. Just simply add all the categories to sw6
        products_in_db = BridgeProductEntity.query.all()
        print("First Sync without parent.")
        for product in products_in_db:
            self.upsert_ntt(product, add_parent=False)
            self.upsert_images_to_sw6(ntt=product)
        return True

    def upsert_images_to_sw6(self, ntt):
        self.print_method_info(self.class_name)

        self.sw6_media_controller.upsert_product_images_to_sw6(ntt=ntt)




