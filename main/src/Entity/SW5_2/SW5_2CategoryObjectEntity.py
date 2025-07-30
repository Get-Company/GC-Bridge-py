from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity


class SW5_2CategoryObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_address(self, address_id):
        url = f"/addresses/{address_id}"
        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving address with ID '{address_id}': {e}")

    def get_categories_by_name(self, name):
        url = f"/categories?filter[name]=" + name
        answer = {
            "success": True,
            "data": "",
            "message": ""
        }
        try:
            response = self.get(url)

            if response["total"] == 0:
                answer["success"] = False
                answer["message"] = f"No Category by name {name} found"
                return answer

            elif response["total"] > 1:
                answer["success"] = True
                answer["message"] = f"More than 1 Categories by name {name} found"
                answer["data"] = response["data"]
                return answer

            else:
                answer["data"] = response["data"]
                answer["message"] = f'Exactly 1 Category found {name}:{response["data"]["name"]}'
                return answer

        except Exception as e:
            logger.info(f'Something went worng, searching Categories by name:{name}')
