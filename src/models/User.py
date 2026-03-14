
from models.data_ingestion import dataclass_type
from schema import *
from exceptions.user_exceptions import *

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

class User:
    def __init__(self, name: str, email = None, phone_number = None, linkedin = None, github = None, other_links = None):
        if not isinstance(name, str) or not name:
            logger.error("Invalid name provided for User initialization.")
            raise ValueError("Name must be a non-empty string")
        contact_details = ContactDetails(name=name, email=email, phone_number=phone_number, linkedin=linkedin, github=github, other_links=other_links) #TODO 
        self.skills = {}
        self.qualifications = {}
        self.person = Person(name=name, cai_hash="USER.PRIMARY", id="USER.PRIMARY", relation_type="USER", is_reference=False, contact_details=contact_details, comment=None) #TODO
        self.projects = {}
        self.placements = {}
        self.hobbies = {}
        self.people = {}

    def add_data(self, data, d_type:dataclass_type):
        registry_map = {
            dataclass_type.SKILL: self.skills,
            dataclass_type.QUALIFICATION: self.qualifications,
            dataclass_type.PERSON: self.people,
            dataclass_type.PROJECT: self.projects,
            dataclass_type.PLACEMENT: self.placements,
            dataclass_type.HOBBY: self.hobbies,
        }
        d = registry_map[d_type]
        pre_length = len(d)
        d[data.id] = data
        #TODO add logger to generic class so all can use it
        logger.debug(f"Added {data.name} to {d_type.value} dictionary. previous length of dict {pre_length}, current legnth {len(d)}")
    def get_dict(self, d_type:dataclass_type):
        match d_type:
            case dataclass_type.SKILL:
                return self.skills
            case dataclass_type.QUALIFICATION:
                return self.qualifications
            case dataclass_type.PERSON:
                return self.people
            case dataclass_type.PROJECT:
                return self.projects
            case dataclass_type.PLACEMENT:
                return self.placements
            case dataclass_type.HOBBY:
                return self.hobbies
            case _:
                raise ValueError(f"Unsupported dataclass type: {d_type}")
        
    def generate_id(self, data, d_type:dataclass_type, hash_suffix_length=0):
        if hash_suffix_length > len(data['cai_hash']):
            raise ValueError("suffix asked for longer than the source data from cai_hash")
        registry_map = {
            dataclass_type.SKILL: data['name'],
            dataclass_type.QUALIFICATION: data['name'],
            dataclass_type.PROJECT: f"{data['name']} {data['cai_hash'][:4]}",  #adds short hash to help differentiate projects with same name
            dataclass_type.PLACEMENT: f"{data['name']} {data['job_title']}", #adds job title to help differentiate placements with same company name
            dataclass_type.HOBBY: data['name'],
            dataclass_type.PERSON: data['cai_hash']
        }
        unconverted_id = registry_map.get(d_type)
        id = str(unconverted_id).lower().replace(" ", "_") + "-" + d_type.value.upper() + data['cai_hash'][0:hash_suffix_length]
        duplicate = self.get_item(id, d_type)
        if duplicate:
            print(f"Warning: Duplicate ID generated for {d_type.value} with name '{data['name']}'.")
            raise ValueError(f"Duplicate entry found in {d_type.value}", duplicate.id)
        return id
    
    def get_item(self, item_id: str, d_type:dataclass_type): #should return item or None if not found
        item = self.get_dict(d_type).get(item_id)
        if not item:
            #TODO logger this as warning
            ItemNotFoundInUserDict(item_id, d_type)
            pass 
        return item
    
    def set_link_skill_to_item(self,item_id: str, skill_id: str, d_type:dataclass_type): #checks if skill exists and if link exists with dataclass. with no matches adds skill_id to dict  
        item = self._validate_link_data(item_id, skill_id, d_type)
        item['related_skills'][skill_id] = skill_id  
    
    def _validate_link_data(self, item_id: str, skill_id: str, d_type:dataclass_type): #helper for set_link_skill_to_item
        item = self.get_item(item_id, d_type)
        if not item:
            raise ItemNotFoundInUserDict(item_id, d_type)
        skill = self.get_item(skill_id, dataclass_type.SKILL)
        if not skill:
            raise SkillNotFoundInUserDict(skill_id,d_type)
        existing_skill_check = item.get_item(skill_id, d_type)
        if existing_skill_check:
            raise SkillLinkAlreadyExists(skill_id, item_id)
        return item

    def hash_search(self, cai_hash):
        reigtry_map = [
            (dataclass_type.SKILL, self.skills),
            (dataclass_type.QUALIFICATION, self.qualifications),
            (dataclass_type.PROJECT, self.projects),
            (dataclass_type.PLACEMENT, self.placements),
            (dataclass_type.HOBBY, self.hobbies),
            (dataclass_type.PERSON, self.people),
        ]
        for d_type, d in reigtry_map:
            for k, v in d.items():
                if v.get('cai_hash') == cai_hash:
                    return v, d_type
        return None


#TODO add in data tooling way to store unassigned items that can then be later processed