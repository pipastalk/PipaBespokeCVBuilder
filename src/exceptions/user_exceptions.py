
from models.data_ingestion import dataclass_type

class ItemNotFoundInUserDict(ValueError):
    def __init__(self, item_id, d_type):
        if d_type == dataclass_type.SKILL:
            raise SkillNotFoundInUserDict(item_id,d_type)
        self.item_id = item_id
        self.d_type = d_type
        super().__init__(f"{d_type.value} with ID '{item_id}' not found in User dictionary.")
class SkillNotFoundInUserDict(ItemNotFoundInUserDict):
    def __init__(self, item_id, d_type):
        super().__init__(item_id, d_type)
class SkillLinkAlreadyExists(ValueError):
    def __init__(self, skill_id, item_id):
        self.skill_id = skill_id
        self.item_id = item_id
        super().__init__(f"Skill with ID '{skill_id}' already linked to item with ID '{item_id}'.")
        