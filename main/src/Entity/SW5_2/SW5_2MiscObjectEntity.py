from main.src.Entity.SW5_2.SW5_2ObjectEntity import SW5_2ObjectEntity


class SW5_2MiscObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_countires(self):
        url = f"/countries"
        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error on loading countries: {e}")

