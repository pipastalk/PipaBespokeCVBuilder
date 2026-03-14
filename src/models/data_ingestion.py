from heapq import merge
import json #only used for CAI hasing as of 2026-03-10
import hashlib
import os
import yaml
import logging
from enum import Enum
from datetime import datetime, date
from schema import *
from User import User
from exceptions.user_exceptions import *

#region logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
full_handler = logging.FileHandler("data/logs/full.log")
local = logging.FileHandler("data/logs/data_ingestion.log")
logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
local.setFormatter(logformat)
full_handler.setFormatter(logformat)
logger.addHandler(full_handler)
logger.addHandler(local)
#endregion

#region generic tools
class dataclass_type(Enum):
    SKILL = "Skill"
    QUALIFICATION = "Qualification"
    CONTACT_DETAILS = "ContactDetails"
    PERSON = "Person"
    PROJECT = "Project"
    PLACEMENT = "Placement"
    LOCATION = "Location"
    ADVERTSOURCE = "AdvertSource"
    ADVERT = "Advert"
    HOBBY = "Hobby"

def read_yaml_file(file_path):
    if not os.path.exists(file_path):
        raise ValueError("The provided source path does not exist")
    with open(file_path, 'r') as file:
        data = list(yaml.safe_load_all(file))
    return data

def validate_data(data,d_type:dataclass_type, user: User):
    #TODO check this item doesn't exist before validating everything?
    validated_data = {}
    required_fields = get_required_fields(d_type)
    date_fields = ['start_date', 'end_date', 'awarded_date', 'expiration_date']
    if not data:
        raise ValueError("Placement was invalid, expected company as base field")
    if not data.get('cai_hash'):
        logger.warning(f"cai_hash not provided for {dataclass_type.value} with name {data['name']}, generating cai_hash")
        data['cai_hash'] = build_cai_hash(data)  
    for field in required_fields:
        if not data[field]:
            logger.error(f"Required field is missing from data, field:{required_fields}")
            raise ValueError(f"Required field is missing from data, field:{required_fields}")
    for field in data:
        if field in date_fields:
            validated_data[field] = convert_date(data[field])
            continue
        match field: #TODO maybe change to registry map
            case "related_skills":
                related_data = create_missing_related_items(data[field], dataclass_type.SKILL, user)
                validated_data[field] = related_data
                continue
            case "related_projects":
                related_data = create_missing_related_items(data[field], dataclass_type.PROJECT, user)
                validated_data[field] = related_data
                continue
            case "related_qualifications":
                related_data = create_missing_related_items(data[field], dataclass_type.QUALIFICATION, user)
                validated_data[field] = related_data
                continue
            case "related_placements":
                related_data = create_missing_related_items(data[field], dataclass_type.PLACEMENT, user)
                validated_data[field] = related_data
                continue
            case "related_hobbies":
                related_data = create_missing_related_items(data[field], dataclass_type.HOBBY, user)
                validated_data[field] = related_data
                continue
            case _:
                validated_data[field] = data[field]
    return validated_data

def create_missing_related_items(data: list, d_type: dataclass_type, user: User):
    items_data = []
    registry_map = {
        dataclass_type.PROJECT: build_project,
        dataclass_type.PLACEMENT: build_placement,
        dataclass_type.QUALIFICATION: build_qualification,
        dataclass_type.HOBBY: build_hobby,
        dataclass_type.SKILL: build_skill
    }
    build = registry_map[d_type]
    for item in data:
        item_cai_hash = build_cai_hash(item)
        item_object = user.hash_search(item_cai_hash)
        if not item_object:
            item_object = build(validate_data(item, d_type, user), user)
        item_id = item_object.get('id')
        if not user.get_item(item_id, d_type): # case is item exists but not within the dict for this dataclass
            raise ValueError("Wrong dataclass_type for the item") #TODO better exception
        items_data.append(item_id)
    return items_data
        
def get_required_fields(d_type:dataclass_type):
    match dataclass_type:
        case dataclass_type.SKILL:
            required_fields = ['name','cai_hash']
        case dataclass_type.QUALIFICATION:
            required_fields = ['name', 'studied_at', 'awarded_date', 'related_skills','cai_hash']
        case dataclass_type.CONTACT_DETAILS:
            required_fields = ['name']
        case dataclass_type.PERSON:
            required_fields = ['name', 'relation_type', 'is_reference', 'cai_hash']
        case dataclass_type.PROJECT:
            required_fields = ['name', 'description','cai_hash']
        case dataclass_type.PLACEMENT:
            required_fields = ['name', 'job_title', 'start_date', 'related_skills','cai_hash']
        case dataclass_type.LOCATION:
            required_fields = ['city', 'country']
        # TODO impliment case dataclass_type.ADVERTSOURCE:
        # TODO impliment case dataclass_type.ADVERT:
        case dataclass_type.HOBBY:
            required_fields = ['name', 'description','cai_hash']
        case _:
            raise ValueError("Invalid dataclass type provided for validation")
    return required_fields

def get_link_skills(skill_data_list, dataclass_type, user: User):
    related_skillset = {}
    #create skills if they do not exist, 
    if not skill_data_list:
        return related_skillset
    for entry in skill_data_list:
        new_cai = build_cai_hash(entry)
        if len(user.skills) == 0: #always add if empty dict
            new_skill = build_skill(validate_data(entry, dataclass_type.SKILL, user), user)
            user.skills[new_skill.id] = new_skill
            related_skillset[new_skill.id] = new_skill.id
            continue
        existing_skills = {}
        for k, skill in user.skills.items():
            existing_skills[skill.cai_hash] = skill
        if new_cai not in existing_skills:
            #validates, builds, then adds to skills list
            new_skill = build_skill(validate_data(entry, dataclass_type.SKILL, user), user)
            user.skills[new_skill.id] = new_skill
        else:
            new_skill = existing_skills[new_cai]
        related_skillset[new_skill.id] = new_skill.id
    return related_skillset

def convert_date(date_field):
    if not date_field:
        return None
    if isinstance(date_field, datetime):
        return date_field.date()
    if not isinstance(date_field, date):
        try:
            date_field = datetime.strptime(date_field, '%d-%m-%Y')
        except ValueError:
            raise ValueError(f"date entered as a string with invalid date format, expected DD-MM-YYYY")
    return date_field

def parse_data(file_path, d_type: dataclass_type, user: User):

    match d_type:
        case dataclass_type.PERSON:
            build = build_person
        case dataclass_type.PLACEMENT:
            build = build_placement
        case dataclass_type.PROJECT:
            build = build_project
        #TODO case dataclass_type.LOCATION:          pass
        #TODO case dataclass_type.ADVERTSOURCE:       pass
        #TODO case dataclass_type.ADVERT:             pass
        case dataclass_type.SKILL:
            build = build_skill
        case dataclass_type.QUALIFICATION:
            build = build_qualification
        case dataclass_type.HOBBY:
            build = build_hobby
        case _:
            raise ValueError("Invalid dataclass type provided for parsing")
    
    file_data = read_yaml_file(file_path)
    for entry in file_data:
        logger.info(f"Parsing {d_type.value} entry: {entry}")
        if not entry:
            raise ValueError(f"Empty entry found in {d_type.value} file, please ensure all entries have data. .yaml files should not end in ---") ##TODO could doa silent error
        validated_data = validate_data(entry, d_type, user)
        if build:
            finished_entry = build(validated_data, user)
            user.add_data(finished_entry, d_type)
        else:
            raise NotImplementedError(f"No build function implemented for {d_type.value}")

def check_for_duplicates(cai_hash, dataclass_type: dataclass_type, user: User): 
    #returns false if no duplicate, returns existing object if duplicate found. Searches via cai_hash not via id
    existing_matches = {}
    registry_map = {
        dataclass_type.SKILL: user.skills,
        dataclass_type.QUALIFICATION: user.qualifications,
        dataclass_type.PROJECT: user.projects,
        dataclass_type.PLACEMENT: user.placements,
        dataclass_type.HOBBY: user.hobbies,
        dataclass_type.PERSON: user.people
    }
    for k, v in registry_map.get(dataclass_type, {}).items():
        existing_matches[v.cai_hash] = v
    if cai_hash in existing_matches:
        return existing_matches[cai_hash]
    return False

def generate_id(data, dataclass_type: dataclass_type, user: User):
    registry_config = {
        dataclass_type.SKILL: {'id': data['name'], 'dict': user.skills},
        dataclass_type.QUALIFICATION: {'id': data['name'], 'dict': user.qualifications},
        dataclass_type.PROJECT: {'id': f"{data['name']} {data['cai_hash'][:4]}", 'dict': user.projects}, #adds short hash to help differentiate projects with same name
        dataclass_type.PLACEMENT: {'id': f"{data['name']} {data['job_title'] if dataclass_type == dataclass_type.PLACEMENT else ''}", 'dict': user.placements}, #adds job title to help differentiate placements with same company name
        dataclass_type.HOBBY: {'id': data['name'], 'dict': user.hobbies},
        dataclass_type.PERSON: {'id': data['cai_hash'], 'dict': user.people}
    }
    target_dict = registry_config[dataclass_type]['dict']
    unconverted_id = registry_config[dataclass_type]['id']
    id = str(unconverted_id).lower().replace(" ", "_") + "-" + dataclass_type.value.upper()
    dupe = check_for_duplicates(data['cai_hash'], dataclass_type, user)
    if dupe is False:
        logger.info(f"Generated new id {id} for {dataclass_type.value} with name {data['name']}")
        attempts = 0
        while id in target_dict: 
            id = str(unconverted_id).lower().replace(" ", "_") + "-" + dataclass_type.value.upper() + "-" + data['cai_hash'][2:(attempts+2)] #adds short hash to ensure unique id, in case of duplicate names. Only added if duplicate found to keep ids clean where possible
            attempts += 1
            if attempts > 12:
                logger.error(f"Duplicate id {id} found for {dataclass_type.value} with name {data['name']}")
                raise ValueError(f"Unable to generate new ID for {dataclass_type.value} with name {data['name']} after 12 attempts.") #TODO handle this better
        return id
    logger.info(f"Duplicate found for {dataclass_type.value} with name {data['name']}, using existing id {dupe.__dict__.get(dataclass_type.value.lower() + '_id')}")
    raise ValueError(f"Duplicate entry found for {dataclass_type.value} with name {data['name']}, please use existing entry {dupe.id}")      

def build_cai_hash(data):
    #Content-Addressable Identifier
    #build dict of all the data
    #conect dict to string
    #hash string to create unique identifier for this data
    #return hash
    # Convert data to a canonical string (sorted keys for consistency)
    data_str = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str) # default=str to handle non-serializable objects like dates
    # Hash the string using SHA-256
    hash_obj = hashlib.sha256(data_str.encode('utf-8'))
    # Return the hex digest as the unique identifier
    return hash_obj.hexdigest()

def merge_matched_data(data, cai_hash, dataclass_type: dataclass_type, user: User):
    #DOING 
    pass
#endregion

#region placements tools
def build_placement(validated_placement, user: User):
    placement = Placement(
        cai_hash=validated_placement['cai_hash'],
        id = generate_id(validated_placement, dataclass_type.PLACEMENT, user),
        company_name=validated_placement['name'],
        job_title=validated_placement['job_title'],
        start_date=validated_placement['start_date'],
        end_date=validated_placement.get('end_date'),
        project_references=validated_placement['related_projects'] if 'related_projects' in validated_placement else {},
        reference_contacts=validated_placement['reference_contacts'] if 'reference_contacts' in validated_placement else None,
        related_skills=validated_placement['related_skills'] if 'related_skills' in validated_placement else {},
        reason_for_leaving=validated_placement['reason_for_leaving'] if 'reason_for_leaving' in validated_placement else None,
    )
    return placement
#endregion

#region skills tools
def build_skill(validated_skill, user: User):
    skill = Skill(
        cai_hash=validated_skill['cai_hash'],
        id = generate_id(validated_skill, dataclass_type.SKILL, user),
        skill_name=validated_skill['name'],
        proficiency_level=validated_skill['proficiency_level'] if 'proficiency_level' in validated_skill else None,
        enjoyment_level=validated_skill['enjoyment_level'] if 'enjoyment_level' in validated_skill else None,
        tags=validated_skill['tags'] if 'tags' in validated_skill else None,
        related_placements=validated_skill['related_placements'] if 'related_placements' in validated_skill else None,
        related_projects=validated_skill['related_projects'] if 'related_projects' in validated_skill else None,
        related_qualifications=validated_skill['related_qualifications'] if 'related_qualifications' in validated_skill else None,
    )
    return skill
#endregion

#region project tools
def build_project(validated_project, user: User):
    project = Project(
        cai_hash=validated_project['cai_hash'],
        id = generate_id(validated_project, dataclass_type.PROJECT, user),
        project_name=validated_project['name'],
        description=validated_project['description'],
        start_date=validated_project['start_date'] if 'start_date' in validated_project else None,
        end_date=validated_project['end_date'] if 'end_date' in validated_project else None,
        related_skills=validated_project['related_skills'] if 'related_skills' in validated_project else {},
        comment=validated_project['comment'] if 'comment' in validated_project else None,
    )
    return project
#endregion

#region hobby tools
def build_hobby(validated_hobby, user: User):
    hobby = Hobby(
        cai_hash = validated_hobby['cai_hash'],
        id = generate_id(validated_hobby, dataclass_type.HOBBY, user),
        hobby_name=validated_hobby['name'],
        description=validated_hobby['description'],
        related_skills=validated_hobby['related_skills'] if 'related_skills' in validated_hobby else {},
        tags=validated_hobby['tags'] if 'tags' in validated_hobby else None,
        awards_or_accolades=validated_hobby['awards_or_accolades'] if 'awards_or_accolades' in validated_hobby else None,
        comment=validated_hobby['comment'] if 'comment' in validated_hobby else None,
    )
    return hobby
#endregion

#region qualification tools
def build_qualification(validated_qualification, user: User):
    qualification = Qualification(
        cai_hash=validated_qualification['cai_hash'],
        id = generate_id(validated_qualification, dataclass_type.QUALIFICATION, user),
        qualification_name=validated_qualification['name'],
        studied_at=validated_qualification['studied_at'],
        awarded_date=validated_qualification['awarded_date'],
        grade = validated_qualification['grade'],
        related_skills=validated_qualification['related_skills'] if 'related_skills' in validated_qualification else {},
        tags=validated_qualification['tags'] if 'tags' in validated_qualification else [],
        expiration_date=validated_qualification['expiration_date'] if 'expiration_date' in validated_qualification else None,
        comment=validated_qualification['comment'] if 'comment' in validated_qualification else None,
    )
    return qualification
#endregion
    
#region people tools
def build_person(validated_person, user: User): #Validates and builds contact details within Person.
    validated_contact_data = validate_data(validated_person['contact_details'], dataclass_type.CONTACT_DETAILS, user)
    person = Person(
        cai_hash=validated_person['cai_hash'],
        id = generate_id(validated_person, dataclass_type.PERSON, user),
        name=validated_person['name'],
        relation_type=validated_person['relation_type'],
        is_reference=validated_person['is_reference'],
        contact_details=build_contact_details(validated_contact_data),
        comment=validated_person['comment'] if 'comment' in validated_person else None,
    )
    return person
#endregion

#region contactdetails tools
#contact details doesn't parse as they are provided within other dataclasses
def build_contact_details(validated_contact_details):
    contact_details = ContactDetails(
        name=validated_contact_details['name'],
        email=validated_contact_details['email'] if 'email' in validated_contact_details else None,
        phone_number=validated_contact_details['phone_number'] if 'phone_number' in validated_contact_details else None,
        linkedin=validated_contact_details['linkedin'] if 'linkedin' in validated_contact_details else None,
        github=validated_contact_details['github'] if 'github' in validated_contact_details else None,
        other_links=validated_contact_details['other_links'] if 'other_links' in validated_contact_details else None,
    )
    return contact_details
#endregion


#region scratch testing
example_user = User(
    name="Pippa",
    email="test@test.com",
    phone_number="1234567890",)


placements_data = parse_data("data/CV_Resources/Personal/placements.yaml", dataclass_type.PLACEMENT, example_user)
skills_data = parse_data("data/CV_Resources/Personal/skills.yaml", dataclass_type.SKILL, example_user)
projects_data = parse_data("data/CV_Resources/Personal/projects.yaml", dataclass_type.PROJECT, example_user)
hobbies_data = parse_data("data/CV_Resources/AI_Example_data/hobbies.yaml", dataclass_type.HOBBY, example_user)
qualifications_data = parse_data("data/CV_Resources/AI_Example_data/qualifications.yaml", dataclass_type.QUALIFICATION, example_user)
people_data = parse_data("data/CV_Resources/AI_Example_data/people.yaml", dataclass_type.PERSON, example_user)



print("x")

#TODO that list of ID's for related should probably be a dict for user search functions, maybe id:cai
#endregion
#TODO when a match is found update any null field with existing ones
#TODO handle generate_id duplicate id's better, currently a short hash could hit limits, not sure if we may hit an additional unhandled error that no more values in cai_hash
#TODO sort the related_projects, related_placements, related_hobbies etc

#TODO fix issue with results of parse_data, works for everything but skills atm but with circular it needs to write to the user not return the data