import logging
from main.src.Entity.ERP.ERPDatasetObjectEntity import ERPDatasetObjectEntity
import datetime

# Tools
from main.src.Repository.functions_repository import find_image_filename_in_path

class ERPArtikelKategorieEntity(ERPDatasetObjectEntity):

    def __init__(self, erp_obj, id_value=None, dataset_range=None):

        self.erp_obj = erp_obj
        self.dataset_name = 'ArtikelKategorien'
        self.dataset_id_field = 'Nr'
        self.dataset_id_value = id_value
        self.dataset_range = dataset_range
        self.prefill_json_directory = None

        # Need to call the __init_of the super class
        super().__init__(
            erp_obj=self.erp_obj,
            dataset_name=self.dataset_name,
            dataset_id_field=self.dataset_id_field,
            dataset_id_value=self.dataset_id_value,
            dataset_range=self.dataset_range,
            prefill_json_directory=self.prefill_json_directory
        )

    def get_images(self):
        """
        Gets the images by the Special COM Query GetEditObject(4).LinkFilename
        Removes the path
        splits the image_file into name and type
        :return: array with objects image.name, image.type
        # Todo: Make it nicer and maybe use DataSet: Bilder ?
        """
        dataset = self.get_created_dataset()

        image_path = dataset.Fields.Item("Bild").GetEditObject(4).LinkFileName
        if image_path:
            image_file = find_image_filename_in_path(image_path)
            image_array = image_file.split('.', 1)

            image = {"name": image_array[0], "type": image_array[1]}

            return image
        else:
            return None


