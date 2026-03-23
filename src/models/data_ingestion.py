import json #only used for CAI hasing as of 2026-03-16
import hashlib
import os
import yaml
import logging
from datetime import datetime, date
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse

from src.models.AdvertSourceType import AdvertSourceType
from src.exceptions.data_ingestion_exceptions import *
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

def validate_contact_details(data):
    blank_contact_details: dict[str, object | None] = {
        'name': None,
        'email': None,
        'phone_number': None,
        'linkedin': None,
        'github': None,
        'other_links': None,
    }
    if not data:
        logger.info("No data passed to validate contact details")
        return blank_contact_details
    validated_data = dict(blank_contact_details)
    validated_data['name'] = data.get('name')
    email = data.get('email')
    if email:
        validated_data['email'] = email
        try:
            validated_email = validate_email(email)
        except EmailNotValidError as e:
            log_and_raise(logger, logging.ERROR, f"Invalid email address: {email}", e)
        
    phone_number = data.get('phone_number')
    if phone_number:
        validated_data['phone_number'] = phone_number
        parsed_number = phonenumbers.parse(phone_number, "UK")
        if not phonenumbers.is_valid_number(parsed_number):
            log_and_raise(logger, logging.ERROR, f"Invalid phone number: {phone_number}", ValueError())
    linkedin_link = data.get('linkedin')
    if linkedin_link:
        if not is_valid_url(linkedin_link):
            log_and_raise(logger, logging.ERROR, f"Invalid LinkedIn URL: {linkedin_link}", ValueError())
        else:
            validated_data['linkedin'] = linkedin_link
    github_link = data.get('github')
    if github_link:
        if not is_valid_url(github_link):
            log_and_raise(logger, logging.ERROR, f"Invalid GitHub URL: {github_link}", ValueError())
        else:
            validated_data['github'] = github_link
    other_links = data.get('other_links')
    if other_links and isinstance(other_links, list):
        validated_other_links = []
        for link in other_links:
            if not is_valid_url(link):
                log_and_raise(logger, logging.ERROR, f"Invalid URL in other_links: {link}", ValueError())
            else:
                validated_other_links.append(link)
        validated_data['other_links'] = validated_other_links
    return validated_data

def validate_location(data):
    if not data:
        log_and_raise(logger, logging.ERROR, "no data passed to validate location", ValueError())
    check_required_fields(dataclass_type.LOCATION, data)
    validated_data = {
        'city': data.get('city'),
        'country': data.get('country'),
    }
    optional_fields = ['address', 'post_or_zip_code', 'gps_coordinates']
    for field in optional_fields:
        if field in data and data.get(field) is not None:
            validated_data[field] = data.get(field)
    return validated_data

def validate_advert_source(data):
    if not data:
        log_and_raise(logger, logging.ERROR, "no data passed to validate advert source", ValueError())
    check_required_fields(dataclass_type.ADVERTSOURCE, data)

    validated_data = {
        'source_path': data.get('source_path'),
        'sourced_from': data.get('sourced_from'),
    }

    source_type = data.get('source_type')
    if source_type is None:
        source_type = determine_advert_type(validated_data['source_path'])
    elif isinstance(source_type, str):
        registry_map = {
            'pdf': AdvertSourceType.PDF,
            'html': AdvertSourceType.WEBSITE,
            'docx': AdvertSourceType.WORD,
        }
        mapped_type = registry_map.get(source_type.lower())
        if not mapped_type:
            msg = f"Unsupported advert source type: {source_type}"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        source_type = mapped_type
    elif not isinstance(source_type, AdvertSourceType):
        msg = f"Unsupported advert source type value: {source_type}"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

    validated_data['source_type'] = source_type
    if data.get('comment') is not None:
        validated_data['comment'] = data.get('comment')
    return validated_data

def validate_advert(data):
    if not data:
        log_and_raise(logger, logging.ERROR, "no data passed to validate advert", ValueError())
    check_required_fields(dataclass_type.ADVERT, data)

    validated_data = {
        'advert_title': data.get('advert_title'),
        'advert_description': data.get('advert_description'),
        'working_pattern': data.get('working_pattern'),
        'advertStyle': data.get('advertStyle'),
        'source': validate_advert_source(data.get('source')),
        'placement_location': validate_location(data.get('placement_location')),
        'contact_details': validate_contact_details(data.get('contact_details', {})),
    }

    # Skills are intentionally kept as raw names for later comparison with user skill names.
    for skill_field in ['required_skills', 'desired_skills']:
        if skill_field not in data:
            continue
        skills = data.get(skill_field)
        if not isinstance(skills, (list, set, tuple)):
            msg = f"{skill_field} must be a list, set, or tuple of skill names"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        if not all(isinstance(skill_name, str) for skill_name in skills):
            msg = f"{skill_field} must contain only skill names as strings"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        validated_data[skill_field] = set(skills)

    return validated_data

def is_valid_url(url):
    try:
        result = urlparse(url)
        # Check if the scheme (http/https) and the domain (netloc) are present
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
#endregion
def validate_data(data,d_type:dataclass_type, user: User):
    if d_type == dataclass_type.CONTACT_DETAILS:
        return validate_contact_details(data)
    if not data:
        log_and_raise(logger, logging.ERROR, "no data passed to validate", ValueError())
    if d_type == dataclass_type.LOCATION:
        return validate_location(data)
    if d_type == dataclass_type.ADVERTSOURCE:
        return validate_advert_source(data)
    if d_type == dataclass_type.ADVERT:
        return validate_advert(data)

    entry_data_hash = build_cai_hash(data)
    result = user.hash_search(entry_data_hash)
    if result:
        matched_id = result[0].id
        matched_d_type = result[1]
        merge_matched_data(data, matched_id, matched_d_type, user)
    validated_data = {}
    if not data.get('cai_hash'): #has to be before required field checks
        validated_data['cai_hash'] = entry_data_hash
        logger.info(
            f"cai_hash was not present in data for {d_type.value} with name "
            f"{data.get('name', '<unnamed>')}, generated cai_hash: {validated_data['cai_hash']}"
        )
    if not data.get('id'): # has to be before related_skills linking
        try:
            validated_data['id'] = generate_unique_id(data, d_type, user, validated_data['cai_hash'])
        except CriticalDuplicateItemExists as e:
            log_and_raise(logger, logging.ERROR, f"Critical duplicate item exists for {d_type.value} with cai_hash {validated_data['cai_hash']}", e)
    date_fields = ['start_date', 'end_date', 'awarded_date', 'expiration_date'] #Used to ensure dates are converted to correct format
    check_required_fields(d_type, data)
    for field, value in data.items():
        if field in date_fields:
            validated_data[field] = convert_date(value)
        elif field in "related_skills":
            link_skill_to_object(value, d_type, validated_data['id'], user)
        else:
            validated_data[field] = value
    return validated_data

def link_skill_to_object(data, d_type, parent_id, user):
    if data and isinstance(data, list):
        for skill in data:
            if isinstance(skill, str):
                skill = {
                    "name": skill
                }
            if not isinstance(skill, dict): 
                msg = f"Related skills format invalid"
                log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
            try:
                validated_skill = validate_data(skill, dataclass_type.SKILL, user)
                skill_to_link = user.get_item(validated_skill['id'], dataclass_type.SKILL)
            except (DuplicateItemExists, MergedDataException) as e:   
                skill_to_link = user.get_item(e.item_id, dataclass_type.SKILL)
                logger.info(f"Related skill already exists, linking to existing skill with id {skill_to_link.id}") 
            if not isinstance(skill_to_link, Skill):
                skill_to_link = build_skill(validated_skill)
                user.add_data(skill_to_link, dataclass_type.SKILL)
            user.add_skill_link(d_type, parent_id, skill_to_link.id) #type: ignore should be confirmed by check if exists

def generate_unique_id(data, d_type, user, cai_hash):
    max_attempts = len(cai_hash)
    for counter in range(max_attempts):
        try:
            return user.generate_id(data, d_type, counter, cai_hash)
        except (DuplicateItemExists, DuplicateItemIDExists) as e:
            discovered_duplicate = user.get_item(e.item_id, d_type)
            if d_type == dataclass_type.SKILL:
                logger.info(f"Duplicate entry found with matching hash, merging data for {d_type.value} with id {discovered_duplicate.id}")
                merge_matched_data(data, e.item_id, e.d_type, user)
                return discovered_duplicate.id
            continue
    raise CriticalDuplicateItemExists(cai_hash, d_type, max_attempts)
        
def check_required_fields(d_type:dataclass_type, data):
    registry_map = { #cai_hash and id are auto-generated so not included in source data checks
        dataclass_type.SKILL: ['name'],
        dataclass_type.QUALIFICATION: ['name', 'studied_at', 'awarded_date', 'related_skills'],
        dataclass_type.CONTACT_DETAILS: [],
        dataclass_type.PERSON: ['name', 'relation_type', 'is_reference'],
        dataclass_type.PROJECT: ['name', 'description'],
        dataclass_type.PLACEMENT: ['name', 'job_title', 'start_date', 'related_skills'],
        dataclass_type.LOCATION: ['city', 'country'],
        dataclass_type.ADVERTSOURCE: ['source_path', 'sourced_from'],
        dataclass_type.ADVERT: [
            'advert_title',
            'advert_description',
            'source',
            'placement_location',
            'working_pattern',
            'advertStyle',
        ],
        dataclass_type.HOBBY: ['name', 'description'],
    }
    if registry_map.get(d_type) and isinstance(registry_map[d_type], list):
        required_fields = registry_map[d_type]
        for field in required_fields:  
            if data.get(field) is None:
                item_name = data.get('name', '<unnamed>')
                msg = f"Required field {field} is missing from data for {d_type.value} with name {item_name}"
                log_and_raise(
                    logger,
                    logging.ERROR,
                    msg,
                    ValueError(msg),
                )
    else:
        msg = f"Unable to retrieve requried_fields. Data cannot be validated, confirm dataclass type is correct. dataclass_type:{d_type}"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
    
    
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
        dataclass_type.LOCATION: build_location,
        dataclass_type.ADVERTSOURCE: build_advert_source,
        dataclass_type.ADVERT: build_advert,
        dataclass_type.SKILL: build_skill,
        dataclass_type.QUALIFICATION: build_qualification,
        dataclass_type.HOBBY: build_hobby,
    }
    build = registry_map.get(d_type)
    if not build:
        msg = f"No build function implemented for {d_type.value}"
        log_and_raise(logger, logging.ERROR, msg, NotImplementedError(msg))
        return #CRITICAL ERROR raised error should prevent hitting this return
    file_data = read_yaml_file(file_path)
    built_entries = []
    non_user_persisted_types = {dataclass_type.LOCATION, dataclass_type.ADVERTSOURCE, dataclass_type.ADVERT}
    for entry in file_data:
        logger.info(f"Parsing {d_type.value} entry: {entry}")
        if not entry:
            msg = f"Empty entry found in {d_type.value} file, please ensure all entries have data. .yaml files should not end in ---"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg)) ##TODO could do a silent error
        try:
            validated_data = validate_data(entry, d_type, user)
        except MergedDataException as e:
            continue #Skipping as no need to build the entry, data was existing and merged.
        if d_type in {dataclass_type.PERSON, dataclass_type.ADVERT}:
            finished_entry = build(validated_data, user)
        else:
            finished_entry = build(validated_data)
        built_entries.append(finished_entry)
        if d_type in non_user_persisted_types:
            continue
        user.add_data(finished_entry, d_type) #Keeping add outside of build to allow for single purpose function and easier unit testing
    return built_entries

def build_cai_hash(data):
    # Convert data to a canonical string (sorted keys for consistency)
    data_str = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str) # default=str to handle non-serializable objects like dates
    # Hash the string using SHA-256
    hash_obj = hashlib.sha256(data_str.encode('utf-8'))
    # Return the hex digest as the unique identifier
    return hash_obj.hexdigest()

def merge_matched_data(data, item_id, d_type: dataclass_type, user: User):
    existing_item  = user.get_item(item_id, d_type)
    if existing_item is None:
        msg = f"Unexpected error during merge: no existing item found via hash search with {data['name']} for {d_type.value}"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
    else:
        none_fields = [field for field in existing_item.__dataclass_fields__ if getattr(existing_item, field) is None]
        for field in none_fields:
            if field in data and data[field] is not None:
                setattr(existing_item, field, data[field])
                logger.info(f"Merged field {field} for {d_type.value} with id {existing_item.id}")
        raise MergedDataException(existing_item.id, d_type)
    
#endregion

#region builds for dataclass objects
def build_placement(validated_placement) -> Placement:
    placement = Placement(
        cai_hash=validated_placement['cai_hash'],
        id = validated_placement['id'],
        name=validated_placement['name'],
        job_title=validated_placement['job_title'],
        start_date=validated_placement['start_date'],
        end_date=validated_placement.get('end_date'),
        related_projects=validated_placement['related_projects'] if 'related_projects' in validated_placement else set(),
        reference_contacts=validated_placement['reference_contacts'] if 'reference_contacts' in validated_placement else set(),
        related_skills=validated_placement['related_skills'] if 'related_skills' in validated_placement else set(),
        reason_for_leaving=validated_placement['reason_for_leaving'] if 'reason_for_leaving' in validated_placement else None,
    )
    return placement

def build_skill(validated_skill) -> Skill:
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

def build_project(validated_project) -> Project:
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

def build_hobby(validated_hobby) -> Hobby:
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

def build_qualification(validated_qualification) -> Qualification:
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

def build_person(validated_person, user: User) -> Person: #Validates and builds contact details within Person.
    validated_contact_data = validate_data(validated_person.get('contact_details', {}), dataclass_type.CONTACT_DETAILS, user)
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
def build_contact_details(validated_contact_details) -> ContactDetails:
    validated_contact_details = validated_contact_details or {}
    contact_details = ContactDetails(
        name=validated_contact_details['name'] if 'name' in validated_contact_details else None,
        email=validated_contact_details['email'] if 'email' in validated_contact_details else None,
        phone_number=validated_contact_details['phone_number'] if 'phone_number' in validated_contact_details else None,
        linkedin=validated_contact_details['linkedin'] if 'linkedin' in validated_contact_details else None,
        github=validated_contact_details['github'] if 'github' in validated_contact_details else None,
        other_links=validated_contact_details['other_links'] if 'other_links' in validated_contact_details else None,
    )
    return contact_details

def build_location(validated_location) -> Location:
    location = Location(
        city=validated_location['city'],
        country=validated_location['country'],
        address=validated_location['address'] if 'address' in validated_location else None,
        post_or_zip_code=validated_location['post_or_zip_code'] if 'post_or_zip_code' in validated_location else None,
        gps_coordinates=validated_location['gps_coordinates'] if 'gps_coordinates' in validated_location else None,
    )
    return location
#endregion

#region adverts
def determine_advert_type(file_path):
    path = file_path.split(".")
    if len(path) < 2:
        msg = f"Unable to determine advert type from file path: {file_path}"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
    file_type = path[-1].lower()
    registry_map = {
        "pdf": AdvertSourceType.PDF,
        "html": AdvertSourceType.WEBSITE,
        "docx": AdvertSourceType.WORD,
    }
    advert_type = registry_map.get(file_type)
    if not advert_type:
        msg = f"Unsupported advert source type: {file_type}"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
    return advert_type

def build_advert_source(validated_advert_source) -> AdvertSource:
    advert_source = AdvertSource(
        source_path=validated_advert_source['source_path'],
        sourced_from=validated_advert_source['sourced_from'],
        source_type=validated_advert_source['source_type'],
        comment=validated_advert_source['comment'] if 'comment' in validated_advert_source else None,
    )
    return advert_source

def build_advert(validated_advert, user: User) -> Advert:
    source_data = validated_advert.get('source', {})
    if not source_data.get('source_type') and source_data.get('source_path'):
        source_data['source_type'] = determine_advert_type(source_data['source_path'])

    contact_data = validate_data(validated_advert.get('contact_details', {}), dataclass_type.CONTACT_DETAILS, user)
    source = build_advert_source(source_data)
    placement_location = build_location(validated_advert['placement_location'])
    advert = Advert(
        advert_title=validated_advert['advert_title'],
        advert_description=validated_advert['advert_description'],
        source=source,
        placement_location=placement_location,
        working_pattern=validated_advert['working_pattern'],
        contact_details=build_contact_details(contact_data),
        advertStyle=validated_advert['advertStyle'],
        required_skills=validated_advert['required_skills'] if 'required_skills' in validated_advert else set(),
        desired_skills=validated_advert['desired_skills'] if 'desired_skills' in validated_advert else set(),
    )
    return advert
    
#endregion 
#region scratch testing
if __name__ == "__main__":
    example_user = User(
        name="Pippa",
        email="test@test.com",
        phone_number="1234567890",
    )

    parse_data("data/CV_Resources/Personal/placements.yaml", dataclass_type.PLACEMENT, example_user)
    parse_data("data/CV_Resources/Personal/skills.yaml", dataclass_type.SKILL, example_user)
    parse_data("data/CV_Resources/Personal/projects.yaml", dataclass_type.PROJECT, example_user)
    parse_data("data/CV_Resources/AI_Example_data/hobbies.yaml", dataclass_type.HOBBY, example_user)
    parse_data("data/CV_Resources/AI_Example_data/qualifications.yaml", dataclass_type.QUALIFICATION, example_user)
    parse_data("data/CV_Resources/AI_Example_data/people.yaml", dataclass_type.PERSON, example_user)

    print("X")
#endregion