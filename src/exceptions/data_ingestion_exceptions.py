from src.models.dataclass_type import dataclass_type


class MergedDataException(Exception):
    def __init__(self, item_id:str, d_type:dataclass_type):
        self.item_id = item_id
        self.d_type = d_type
        super().__init__(f"Data merged with existing item with id {item_id} in {d_type.value}")