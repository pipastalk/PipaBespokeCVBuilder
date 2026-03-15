import logging
from src.models.dataclass_type import dataclass_type 
logger = logging.getLogger("src.models.User")

class ItemNotFoundInUserDict(ValueError):
    def __init__(self, item_id, d_type, log_level=logging.WARNING):
        self.item_id = item_id
        self.d_type = d_type
        self.message = f"{d_type.value} with ID '{item_id}' not found in User dictionary."
        if d_type == dataclass_type.SKILL and type(self) is ItemNotFoundInUserDict:
            logger.log(log_level, f"Developer Hint: Use SkillNotFoundInUserDict for SKILL types.")
            
        logger.log(log_level, self.message)
        super().__init__(self.message)

class SkillNotFoundInUserDict(ItemNotFoundInUserDict):
    def __init__(self, item_id, d_type, log_level=logging.ERROR):
        super().__init__(item_id, d_type)

class SkillLinkAlreadyExists(ValueError):
    def __init__(self, skill_id, item_id, log_level=logging.ERROR):
        self.skill_id = skill_id
        self.item_id = item_id
        self.message = f"Skill with ID '{skill_id}' is already linked to item with ID '{item_id}'."
        logger.log(log_level, self.message)
        super().__init__(self.message)
