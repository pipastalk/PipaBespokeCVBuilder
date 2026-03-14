import logging

from src.models.dataclass_type import dataclass_type 

#region logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
full_handler = logging.FileHandler("data/logs/full.log")
local = logging.FileHandler("data/logs/user.log")
logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
local.setFormatter(logformat)
full_handler.setFormatter(logformat)
logger.addHandler(full_handler)
logger.addHandler(local)
#endregion

class ItemNotFoundInUserDict(ValueError):
    def __init__(self, item_id, d_type, log_level=logging.WARNING):
        if d_type == dataclass_type.SKILL:
            raise SkillNotFoundInUserDict(item_id,d_type)
        self.item_id = item_id
        self.d_type = d_type
        self.message =f"{d_type.value} with ID '{item_id}' not found in User dictionary."
        logger.log(log_level, self.message)
        super().__init__(self.message)

class SkillNotFoundInUserDict(ItemNotFoundInUserDict):
    def __init__(self, item_id, d_type):
        super().__init__(item_id, d_type)

class SkillLinkAlreadyExists(ValueError):
    def __init__(self, skill_id, item_id, log_level=logging.ERROR):
        self.skill_id = skill_id
        self.item_id = item_id
        self.message = f"Skill with ID '{skill_id}' is already linked to item with ID '{item_id}'."
        logger.log(log_level, self.message)
        super().__init__(self.message)
