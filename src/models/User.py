import data
from models.data_ingestion import dataclass_type
from schema import *
class User:
    def __init__(self, name: str, email = None, phone_number = None, linkedin = None, github = None, other_links = None):
        contact_details = ContactDetails(name=name, email=email, phone_number=phone_number, linkedin=linkedin, github=github, other_links=other_links) #TODO 
        self.skills = {}
        self.qualifications = {}
        self.person = Person(name=name, cai_hash="USER.PRIMARY", id="USER.PRIMARY", relation_type="USER", is_reference=False, contact_details=contact_details, comment=None) #TODO
        self.projects = {}
        self.placements = {}
        self.hobbies = {}
        self.people = {}

    def add_data(self, data, d_type:dataclass_type):
        if d_type == dataclass_type.SKILL:
            self.skills[data.id] = data
        elif d_type == dataclass_type.QUALIFICATION:
            self.qualifications[data.id] = data
        elif d_type == dataclass_type.PERSON:
            self.people[data.id] = data
        elif d_type == dataclass_type.PROJECT:
            self.projects[data.id] = data
        elif d_type == dataclass_type.PLACEMENT:
            self.placements[data.id] = data
        elif d_type == dataclass_type.HOBBY:
            self.hobbies[data.id] = data
        else:
            raise ValueError(f"Unsupported dataclass type: {d_type}")
    
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
        duplicate = self.get_dict(d_type).get(id)
        if duplicate:
            print(f"Warning: Duplicate ID generated for {d_type.value} with name '{data['name']}'.")
            raise ValueError(f"Duplicate entry found in {d_type.value}", duplicate.id)
        return id