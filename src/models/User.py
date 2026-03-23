from src.models.schema import *
from src.exceptions.user_exceptions import *
from src.models.dataclass_type import dataclass_type
from src.logging import log_and_raise
#region logging setup
logger = logging.getLogger(__name__)
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
        logger.info(f"Added {data.name} to {d_type.value} dictionary. previous length of dict {pre_length}, current legnth {len(d)}")
    
    def get_dict(self, d_type:dataclass_type):
        registry_map = {
            dataclass_type.SKILL: self.skills,
            dataclass_type.QUALIFICATION: self.qualifications,
            dataclass_type.PERSON: self.people,
            dataclass_type.PROJECT: self.projects,
            dataclass_type.PLACEMENT: self.placements,
            dataclass_type.HOBBY: self.hobbies,
        }
        d = registry_map.get(d_type)
        if d is None:
            raise ValueError(f"Unsupported dataclass type: {d_type}")
        return d
        
    def generate_id(self, data, d_type:dataclass_type, hash_suffix_length=0, cai_hash=None): #I don't like passing cai_hash manually but it's solving a headache with linking skills
        if not cai_hash:
            cai_hash = data['cai_hash']
        if hash_suffix_length > len(cai_hash):
            raise ValueError("suffix asked for longer than the  source data from cai_hash")
        registry_map = {
            dataclass_type.SKILL: data['name'],
            dataclass_type.QUALIFICATION: data['name'],
            dataclass_type.PROJECT: f"{data['name']}-{cai_hash[:4]}",  #adds short hash to help differentiate projects with same name
            dataclass_type.PLACEMENT: f"{data['name']}-{data['job_title'] if 'job_title' in data else 'INVALID'}", #adds job title to help differentiate placements with same company name
            dataclass_type.HOBBY: data['name'],
            dataclass_type.PERSON: cai_hash,
            dataclass_type.CONTACT_DETAILS: cai_hash
        }
        unconverted_id: str = registry_map.get(d_type, "-INVALID") 
        if unconverted_id.endswith("-INVALID"):
            msg = f"Invalid data for ID generation in {d_type.value}: {data['name']}, e.g. missing job title for placement"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        id = str(unconverted_id).lower().replace(" ", "_") + "-" + cai_hash[0:hash_suffix_length] + "-" + d_type.value.upper()
        if d_type == dataclass_type.CONTACT_DETAILS:
            return id # Contacts never are enetered into a colelction, no need for unique checks 
        duplicate = self.get_item(id, d_type)
        if duplicate:
            log_and_raise(logger, logging.ERROR, f"Duplicate entry found in {d_type.value} with id {id}", DuplicateItemIDExists(item_id=id, d_type=d_type))
        return id
    
    def get_item(self, item_id: str, d_type:dataclass_type): #should return item or None if not found
        item = self.get_dict(d_type).get(item_id)
        if not item:
            return None 
        return item
    def get_item_unknown_type(self, item_id: str): #returns tuple of item, dataclass_type or None if not found
        registry_map = [
            (dataclass_type.SKILL, self.skills),
            (dataclass_type.QUALIFICATION, self.qualifications),
            (dataclass_type.PROJECT, self.projects),
            (dataclass_type.PLACEMENT, self.placements),
            (dataclass_type.HOBBY, self.hobbies),
            (dataclass_type.PERSON, self.people),
        ]
        for d_type, d in registry_map:
            item = d.get(item_id)
            if item:
                return item, d_type
        return None
    def add_skill_link(self, related_d_type:dataclass_type, related_item_id: str, skill_id: str):
        skill: Skill = self.get_item(skill_id, dataclass_type.SKILL) #type: ignore
        if not skill:
            log_and_raise(logger, logging.ERROR, f"Skill with id {skill_id} not found when trying to link to {related_d_type.value} with id {related_item_id}", SkillNotFoundInUserDict)
        registry_map = {
            dataclass_type.QUALIFICATION: skill.related_qualifications,
            dataclass_type.PROJECT: skill.related_projects,
            dataclass_type.PLACEMENT: skill.related_placements,
            dataclass_type.HOBBY: skill.related_hobbies,
        }
        related_items_set = registry_map.get(related_d_type)
        if isinstance(related_items_set, set): #Expected True
            related_items_set.add(related_item_id)
            return
        #ERROR CASE HERE ONWARDS
        msg = f"Unsupported dataclass type for skill linking: {related_d_type}"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        
        raise NotImplementedError("This method is not implemented yet")

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
                if v.cai_hash == cai_hash:
                    return v, d_type
        return None


#TODO check raises of custom exceptions to ensure parameters are passed
