import os
import yaml
import logging
from enum import Enum
from datetime import datetime, date
from schema import *
from User import User
#region logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
data_injest_file_log = logging.FileHandler("data/logs/data_ingestion.log")
logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
data_injest_file_log.setFormatter(logformat)
logger.addHandler(data_injest_file_log)
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

def validate_data(data, dataclass_type, user):
    validated_data = {}
    working_data = data # can be overwritten by switch case if needed
    match dataclass_type:
        case dataclass_type.SKILL:
            required_fields = ['skill_name']
        case dataclass_type.QUALIFICATION:
            required_fields = ['qualification_name', 'studied_at', 'awarded_date', 'related_skills']
        case dataclass_type.CONTACT_DETAILS:
            required_fields = ['name']
        case dataclass_type.PERSON:
            required_fields = ['name', 'relation_type', 'is_reference']
        case dataclass_type.PROJECT:
            required_fields = ['name', 'description']
        case dataclass_type.PLACEMENT:
            required_fields = ['name', 'job_title', 'start_date', 'related_skills']
        case dataclass_type.LOCATION:
            required_fields = ['city', 'country']
        # TODO impliment case dataclass_type.ADVERTSOURCE:
        # TODO impliment case dataclass_type.ADVERT:
        case dataclass_type.HOBBY:
            required_fields = ['hobby_name', 'description']
        case _:
            raise ValueError("Invalid dataclass type provided for validation")

    if not working_data:
        raise ValueError("Placement was invalid, expected company as base field")
    for field in working_data:
        if field in required_fields:
            if not working_data[field] and (not isinstance(working_data[field], bool)): #to allow boolean false values to be valid
                raise ValueError(f"No {field} in placement company")
        match field:
            case "start_date": 
                start_date = convert_date(working_data[field])
                validated_data[field] = start_date
                continue
            case "end_date":    
                end_date = convert_date(working_data[field])
                validated_data[field] = end_date
                continue
            case "awarded_date":
                awarded_date = convert_date(working_data[field])
                validated_data[field] = awarded_date
                continue
            case "expiration_date":
                expiration_date = convert_date(working_data[field])
                validated_data[field] = expiration_date
                continue
            case "related_skills":
                #TODO HERE
                skillset = [] 
                for skill in working_data[field]:
                    if skill not in user.skills:
                        t_skill = build_skill(validate_data(skill, dataclass_type.SKILL, user)) #TODO need to ensure verified data
                        user.skills.append(t_skill)
                    else:
                        t_skill = user.skills[user.skills.index(skill)]
                    skillset.append(t_skill['id'])
                    
                match dataclass_type:
                    case dataclass_type.PLACEMENT:
                        validated_data[field] = skillset
                        continue
                    case dataclass_type.QUALIFICATION:
                        validated_data[field] = skillset
                        continue
                    case dataclass_type.HOBBY:
                        validated_data[field] = skillset
                        continue
                    case _:
                        pass
        #TODO work out this as it's circular. Need to have it added to user.skills but also have it added to current types related_skills via id / name combo. Same to do for projects
                
                ##        
                pass
            case "related_projects":
                ## TODO impliment project link
                ##for project in working_data[field]:
                ##    if project not in user.projects:
                ##        user.projects.append(build_project())
                pass
            case _:
                validated_data[field] = working_data[field]
    return validated_data

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

def parse_data(file_path, data_type: dataclass_type):
    #TODO correct yaml data to be uniform so no placement['company'] / skill difference in data then convert parses into using this shared helper.
    build = None
    finished_data = []
    match data_type:
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
        logger.info(f"Parsing {data_type.value} entry: {entry}")
        if not entry:
            raise ValueError(f"Empty entry found in {data_type.value} file, please ensure all entries have data. .yaml files should not end in ---")
        
        
        validated_data = validate_data(entry, data_type)
        if build:
            finished_entry = build(validated_data)
            finished_data.append(finished_entry)
        else:
            raise NotImplementedError(f"No build function implemented for {data_type.value}")
        
    if not finished_data:
         raise ValueError(f"No valid {data_type.value} entries found in file")
    return finished_data
    
#endregion

#region placements tools
def build_placement(validated_placement):
    placement = Placement(
        company_name=validated_placement['name'],
        job_title=validated_placement['job_title'],
        start_date=validated_placement['start_date'],
        end_date=validated_placement.get('end_date'),
        project_references=validated_placement['related_projects'] if 'related_projects' in validated_placement else [],
        reference_contacts=validated_placement['reference_contacts'] if 'reference_contacts' in validated_placement else None,
        related_skills=validated_placement['related_skills'] if 'related_skills' in validated_placement else [],
        reason_for_leaving=validated_placement['reason_for_leaving'] if 'reason_for_leaving' in validated_placement else None,
    )
    return placement
#endregion

#region skills tools
def build_skill(validated_skill):
    skill = Skill(
        skill_name=validated_skill['skill_name'],
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
def build_project(validated_project):
    project = Project(
        project_name=validated_project['project_name'],
        description=validated_project['description'],
        start_date=validated_project['start_date'] if 'start_date' in validated_project else None,
        end_date=validated_project['end_date'] if 'end_date' in validated_project else None,
        related_skills=validated_project['related_skills'] if 'related_skills' in validated_project else [],
        comment=validated_project['comment'] if 'comment' in validated_project else None,
    )
    return project
#endregion

#region hobby tools
def build_hobby(validated_hobby):
    hobby = Hobby(
        hobby_name=validated_hobby['hobby_name'],
        description=validated_hobby['description'],
        related_skills=validated_hobby['related_skills'] if 'related_skills' in validated_hobby else [],
        tags=validated_hobby['tags'] if 'tags' in validated_hobby else None,
        awards_or_accolades=validated_hobby['awards_or_accolades'] if 'awards_or_accolades' in validated_hobby else None,
        comment=validated_hobby['comment'] if 'comment' in validated_hobby else None,
    )
    return hobby
#endregion

#region qualification tools
def build_qualification(validated_qualification):
    qualification = Qualification(
        qualification_name=validated_qualification['qualification_name'],
        studied_at=validated_qualification['studied_at'],
        awarded_date=validated_qualification['awarded_date'],
        grade = validated_qualification['grade'],
        related_skills=validated_qualification['related_skills'] if 'related_skills' in validated_qualification else [],
        tags=validated_qualification['tags'] if 'tags' in validated_qualification else [],
        expiration_date=validated_qualification['expiration_date'] if 'expiration_date' in validated_qualification else None,
        comment=validated_qualification['comment'] if 'comment' in validated_qualification else None,
    )
    return qualification
#endregion

#region people tools
def build_person(validated_person): #Validates and builds contact details within Person.
    validated_contact_data = validate_data(validated_person['contact_details'], dataclass_type.CONTACT_DETAILS)
    person = Person(
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




placements_data = parse_data("data/CV_Resources/Personal/placements.yaml", dataclass_type.PLACEMENT)
skills_data = parse_data("data/CV_Resources/Personal/skills.yaml", dataclass_type.SKILL)
projects_data = parse_data("data/CV_Resources/Personal/projects.yaml", dataclass_type.PROJECT)
hobbies_data = parse_data("data/CV_Resources/AI_Example_data/hobbies.yaml", dataclass_type.HOBBY)
qualifications_data = parse_data("data/CV_Resources/AI_Example_data/qualifications.yaml", dataclass_type.QUALIFICATION)
people_data = parse_data("data/CV_Resources/AI_Example_data/people.yaml", dataclass_type.PERSON)



example_user = User(
    name="Pippa",
    email="test@test.com",
    phone_number="1234567890",)

example_user.placements = placements_data
example_user.skills = skills_data
example_user.projects = projects_data
example_user.hobbies = hobbies_data
example_user.qualifications = qualifications_data
example_user.people = people_data

print("X")
