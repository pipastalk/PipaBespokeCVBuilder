import json #only used for CAI hasing as of 2026-03-16
import hashlib
import os
import yaml
import logging
from datetime import datetime, date

from src.models.dataclass_type import dataclass_type
from src.models.schema import *
from src.models.User import User
from src.exceptions.user_exceptions import *
from src.logging import log_and_raise


#region logging setup
logger = logging.getLogger(__name__)
#endregion

#region generic tools
def read_yaml_file(file_path):
    if not os.path.exists(file_path):
        raise ValueError("The provided source path does not exist")
    with open(file_path, 'r') as file:
        data = list(yaml.safe_load_all(file))
    return data

def validate_data(data,d_type:dataclass_type, user: User):
    if not data:
        log_and_raise(logger, logging.ERROR, "no data passed to validate", ValueError)
    entry_data_hash = build_cai_hash(data)
    result = user.hash_search(entry_data_hash)
    if result:
        # TODO: decide whether to merge duplicates instead of failing hard.
        logger.error(
            f"hash found to be matching existing entry. Duplicate data entry. "
            f"existing id: {result[0].id}, new entry data: {data.get('name', '<unnamed>')}"
        )
        raise DuplicateItemExists(result[0].id, d_type)
    validated_data = {}
    if not data.get('cai_hash'): #has to be before required field checks
        validated_data['cai_hash'] = build_cai_hash(data)
        data['cai_hash'] = validated_data['cai_hash']
        logger.info(
            f"cai_hash was not present in data for {d_type.value} with name "
            f"{data.get('name', '<unnamed>')}, generated cai_hash: {validated_data['cai_hash']}"
        )
    date_fields = ['start_date', 'end_date', 'awarded_date', 'expiration_date'] #Used to ensure dates are converted to correct format
    required_fields = get_required_fields(d_type)
    for field in required_fields:  # pyright: ignore[reportOptionalIterable] - this should either raise a ValueError upon call or return valid list
        if not data.get(field):
            item_name = data.get('name', '<unnamed>')
            log_and_raise(
                logger,
                logging.ERROR,
                f"Required field {field} is missing from data for {d_type.value} with name {item_name}",
                ValueError,
            )
    RELATED_FIELD_MAP = {
        "related_skills": dataclass_type.SKILL,
        "related_projects": dataclass_type.PROJECT,
        "related_qualifications": dataclass_type.QUALIFICATION,
        "related_placements": dataclass_type.PLACEMENT,
        "related_hobbies": dataclass_type.HOBBY,
    }       
    for field, value in data.items():
        if field in date_fields:
            validated_data[field] = convert_date(value)
        elif field == 'id':
            validated_data[field] = generate_unique_id(data, d_type, user)
        elif field in RELATED_FIELD_MAP:
            target_type = RELATED_FIELD_MAP[field]
            validated_data[field] = create_missing_related_items(value, target_type, user)
        else:
            validated_data[field] = value
    return validated_data

def generate_unique_id(data, d_type, user):
    max_attempts = len(data['cai_hash'])
    for counter in range(max_attempts):
        try:
            return user.generate_id(data, d_type, counter)
        except (DuplicateItemExists, DuplicateItemIDExists):
            continue
    raise CriticalDuplicateItemExists(data['cai_hash'], d_type, max_attempts)

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
        search_result = user.hash_search(item_cai_hash) #returns tuple of item, dataclass_type or None if not found
        if not search_result:
            item_object = build(validate_data(item, d_type, user))
            user.add_data(item_object, d_type)
        else: 
            item_object = search_result[0]
        item_id = item_object.id
        if not user.get_item(item_id, d_type): # check for item exists but not within the dict for this dataclass. e.g. Project cai_hash in user.placements set
            log_and_raise(logger, logging.ERROR, "Wrong dataclass_type for the item", ValueError) #TODO better exception
        items_data.append(item_id)

    return items_data
        
def get_required_fields(d_type:dataclass_type):
    registry_map = {
        dataclass_type.SKILL: ['name', 'cai_hash'],
        dataclass_type.QUALIFICATION: ['name', 'studied_at', 'awarded_date', 'related_skills', 'cai_hash'],
        dataclass_type.CONTACT_DETAILS: ['name'],
        dataclass_type.PERSON: ['name', 'relation_type', 'is_reference', 'cai_hash'],
        dataclass_type.PROJECT: ['name', 'description', 'cai_hash'],
        dataclass_type.PLACEMENT: ['name', 'job_title', 'start_date', 'related_skills', 'cai_hash'],
        dataclass_type.LOCATION: ['city', 'country'],
        # TODO dataclass_type.ADVERTSOURCE: [...],
        # TODO dataclass_type.ADVERT: [...],
        dataclass_type.HOBBY: ['name', 'description', 'cai_hash'],
    }
    required_fields = registry_map.get(d_type)
    if not required_fields:
        log_and_raise(logger, logging.ERROR, f"Unable to retrieve requried_fields. Data cannot be validated, confirm dataclass type is correct. dataclass_type:{d_type}", ValueError)
    return required_fields

def convert_date(date_field):
    if not date_field:
        return None
    if isinstance(date_field, datetime):
        return date_field.date()
    if not isinstance(date_field, date):
        try:
            date_field = datetime.strptime(date_field, '%d-%m-%Y').date()
        except ValueError:
            raise ValueError(f"date entered as a string with invalid date format, expected DD-MM-YYYY")
    return date_field

def parse_data(file_path, d_type: dataclass_type, user: User):
    registry_map = {
        dataclass_type.PERSON: build_person,
        dataclass_type.PLACEMENT: build_placement,
        dataclass_type.PROJECT: build_project,
        #TODO dataclass_type.LOCATION: build_location,
        #TODO dataclass_type.ADVERTSOURCE: build_advert_source,
        #TODO dataclass_type.ADVERT: build_advert,
        dataclass_type.SKILL: build_skill,
        dataclass_type.QUALIFICATION: build_qualification,
        dataclass_type.HOBBY: build_hobby,
    }
    build = registry_map.get(d_type)
    if not build:
        log_and_raise(logger, logging.ERROR, f"No build function implemented for {d_type.value}", NotImplementedError)
        return #CRITICAL ERROR raised error should prevent hitting this return
    file_data = read_yaml_file(file_path)
    for entry in file_data:
        logger.info(f"Parsing {d_type.value} entry: {entry}")
        if not entry:
            log_and_raise(logger, logging.ERROR, f"Empty entry found in {d_type.value} file, please ensure all entries have data. .yaml files should not end in ---", ValueError) ##TODO could do a silent error
        validated_data = validate_data(entry, d_type, user)
        if d_type == dataclass_type.PERSON:
            finished_entry = build(validated_data, user)
        else:
            finished_entry = build(validated_data)
        user.add_data(finished_entry, d_type) #Keeping add outside of build to allow for single purpose function and easier unit testing

def build_cai_hash(data):
    # Convert data to a canonical string (sorted keys for consistency)
    data_str = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str) # default=str to handle non-serializable objects like dates
    # Hash the string using SHA-256
    hash_obj = hashlib.sha256(data_str.encode('utf-8'))
    # Return the hex digest as the unique identifier
    return hash_obj.hexdigest()

def merge_matched_data(data, cai_hash, dataclass_type: dataclass_type, user: User):
    #TODO 
    pass
#endregion

#region builds for dataclass objects
def build_placement(validated_placement):
    placement = Placement(
        cai_hash=validated_placement['cai_hash'],
        id = validated_placement['id'],
        name=validated_placement['name'],
        job_title=validated_placement['job_title'],
        start_date=validated_placement['start_date'],
        end_date=validated_placement.get('end_date'),
        project_references=validated_placement['related_projects'] if 'related_projects' in validated_placement else set(),
        reference_contacts=validated_placement['reference_contacts'] if 'reference_contacts' in validated_placement else set(),
        related_skills=validated_placement['related_skills'] if 'related_skills' in validated_placement else set(),
        reason_for_leaving=validated_placement['reason_for_leaving'] if 'reason_for_leaving' in validated_placement else None,
    )
    return placement

def build_skill(validated_skill):
    skill = Skill(
        cai_hash=validated_skill['cai_hash'],
        id = validated_skill['id'],
        name=validated_skill['name'],
        proficiency_level=validated_skill['proficiency_level'] if 'proficiency_level' in validated_skill else None,
        enjoyment_level=validated_skill['enjoyment_level'] if 'enjoyment_level' in validated_skill else None,
        tags=validated_skill['tags'] if 'tags' in validated_skill else set(),
        related_placements=validated_skill['related_placements'] if 'related_placements' in validated_skill else set(),
        related_projects=validated_skill['related_projects'] if 'related_projects' in validated_skill else set(),
        related_qualifications=validated_skill['related_qualifications'] if 'related_qualifications' in validated_skill else set(),
    )
    return skill

def build_project(validated_project):
    project = Project(
        cai_hash=validated_project['cai_hash'],
        id = validated_project['id'],
        name=validated_project['name'],
        description=validated_project['description'],
        start_date=validated_project['start_date'] if 'start_date' in validated_project else None,
        end_date=validated_project['end_date'] if 'end_date' in validated_project else None,
        related_skills=validated_project['related_skills'] if 'related_skills' in validated_project else set(),
        comment=validated_project['comment'] if 'comment' in validated_project else None,
    )
    return project

def build_hobby(validated_hobby):
    hobby = Hobby(
        cai_hash = validated_hobby['cai_hash'],
        id = validated_hobby['id'],
        name=validated_hobby['name'],
        description=validated_hobby['description'],
        related_skills=validated_hobby['related_skills'] if 'related_skills' in validated_hobby else set(),
        tags=validated_hobby['tags'] if 'tags' in validated_hobby else set(),
        awards_or_accolades=validated_hobby['awards_or_accolades'] if 'awards_or_accolades' in validated_hobby else set(),
        comment=validated_hobby['comment'] if 'comment' in validated_hobby else None,
    )
    return hobby

def build_qualification(validated_qualification):
    qualification = Qualification(
        cai_hash=validated_qualification['cai_hash'],
        id = validated_qualification['id'],
        name=validated_qualification['name'],
        studied_at=validated_qualification['studied_at'],
        awarded_date=validated_qualification['awarded_date'],
        grade = validated_qualification['grade'],
        related_skills=validated_qualification['related_skills'] if 'related_skills' in validated_qualification else set(),
        tags=validated_qualification['tags'] if 'tags' in validated_qualification else set(),
        expiration_date=validated_qualification['expiration_date'] if 'expiration_date' in validated_qualification else None,
        comment=validated_qualification['comment'] if 'comment' in validated_qualification else None,
    )
    return qualification

def build_person(validated_person, user: User): #Validates and builds contact details within Person.
    validated_contact_data = validate_data(validated_person['contact_details'], dataclass_type.CONTACT_DETAILS, user)    
    person = Person(
        cai_hash=validated_person['cai_hash'],
        id = validated_person['id'],
        name=validated_person['name'],
        relation_type=validated_person['relation_type'],
        is_reference=validated_person['is_reference'],
        contact_details=build_contact_details(validated_contact_data),
        comment=validated_person['comment'] if 'comment' in validated_person else None,
    )
    return person

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
"""
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
"""
#endregion

#TODO when a match is found update any null field with existing ones