import os
import yaml
from enum import Enum
from datetime import datetime
from schema import *

#region generic tools
class dataclass_type(Enum):
    COMPANY = "Company"
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

def validate_data(data, dataclass_type):
    validated_data = {}
    working_data = None
    match dataclass_type:
        case dataclass_type.COMPANY:
            working_data = data
            required_fields = ['company_name', 'size']
        case dataclass_type.PERSON:
            working_data = data
            required_fields = ['name', 'relation_type', 'is_reference']
        case dataclass_type.PLACEMENT:
            working_data = data['company']
            required_fields = ['name', 'start_date', 'job_title', 'related_skills']
        case dataclass_type.PROJECT:
            working_data = data
            required_fields = ['name', 'description']
        case dataclass_type.LOCATION:
            working_data = data['location']
            required_fields = ['city', 'country']
        # TODO impliment case dataclass_type.ADVERTSOURCE:
        #TODO impliment case dataclass_type.ADVERT:
        case dataclass_type.SKILL:
            working_data = data['skill']
            required_fields = ['skill_name']
        case dataclass_type.QUALIFICATION:
            working_data = data
            required_fields = ['qualification_name', 'institution', 'date_obtained', 'related_skills']
        case dataclass_type.HOBBY:
            working_data = data
            required_fields = ['hobby_name', 'description', 'related_skills']
        case dataclass_type.CONTACT_DETAILS:
            working_data = data
            required_fields = ['email']
        case _:
            raise ValueError("Invalid dataclass type provided for validation")

    if not working_data:
        raise ValueError("Placement was invalid, expected company as base field")
    for field in working_data:
        if field in required_fields:
            if not working_data[field] and (not isinstance(working_data[field], bool)): #to allow boolean false values to be valid
                raise ValueError(f"No {field} in placement company")
        if field == "start_date":
            try:
                # Check if the date is in the correct format (DD-MM-YYYY)
                start_date = datetime.strptime(working_data[field], '%d-%m-%Y')
                validated_data[field] = start_date
                continue
            except ValueError:
                raise ValueError(f"Invalid date format for {field} in placement company, expected DD-MM-YYYY")
        if field == "end_date" and working_data[field]: #end date is optional, but if provided should be in the correct format
            try:
                end_date = datetime.strptime(working_data[field], '%d-%m-%Y')
                validated_data[field] = end_date
                continue
            except ValueError:
                raise ValueError(f"Invalid date format for {field} in placement company, expected DD-MM-YYYY")
        if field == "related_skills":
            ##for skill in working_data[field]:
            ##    if skill not in skillset:
            ##        s = build_skill()
            ##        skillset[skill][placements].append(placement['company']['name'])
            pass
        if field == "related_projects":
            ## TODO impliment project link
            ##for project in working_data[field]:
            ##    if project not in projectset:
            ##        p = build_project()
            ##        projectset[project][placements].append(placement['company']['name'])
            pass
        validated_data[field] = working_data[field]
    return validated_data

def parse_data(file_path, data_type: dataclass_type):
    #TODO correct yaml data to be uniform so no placement['company'] / skill difference in data then convert parses into using this shared helper.
    build = None
    finished_data = []
    match data_type:
        case dataclass_type.COMPANY:
            build = build_company
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
        case dataclass_type.HOBBY:            pass
        case _:
            raise ValueError("Invalid dataclass type provided for parsing")
    
    file_data = read_yaml_file(file_path)
    for entry in file_data:
        print(f"{data_type.value} Name: {entry}")
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
def parse_placements(file_path):
    placements = []
    file_data = read_yaml_file(file_path)
    for placement in file_data:
        print(f"Placement Names {placement['company']['name']}")
        validated_placement = validate_placement_data(placement)
        finished_placement = build_placement(validated_placement)
        placements.append(finished_placement)
    return placements

def validate_placement_data(placement): #helper function to validate data inside placements. Use before build_placement()
    validated_placement = {}
    required_fields = ['name', 'start_date', 'job_title', 'related_skills'] 
    if not placement['company']:
        raise ValueError("Placement was invalid, expected company as base field")
    for field in placement['company']:
        if field in required_fields:
            if not placement['company'][field]:
                raise ValueError(f"No {field} in placement company")
        if field == "start_date":
            try:
                # Check if the date is in the correct format (DD-MM-YYYY)
                start_date = datetime.strptime(placement['company'][field], '%d-%m-%Y')
                validated_placement[field] = start_date
                continue
            except ValueError:
                raise ValueError(f"Invalid date format for {field} in placement company, expected DD-MM-YYYY")
        if field == "end_date" and placement['company'][field]: #end date is optional, but if provided should be in the correct format
            try:
                end_date = datetime.strptime(placement['company'][field], '%d-%m-%Y')
                validated_placement[field] = end_date
                continue
            except ValueError:
                raise ValueError(f"Invalid date format for {field} in placement company, expected DD-MM-YYYY")
        if field == "related_skills":
            ##for skill in placement['company'][field]:
            ##    if skill not in skillset:
            ##        s = build_skill()
            ##        skillset[skill][placements].append(placement['company']['name'])
            pass
        if field == "related_projects":
            ## TODO impliment project link
            ##for project in placement['company'][field]:
            ##    if project not in projectset:
            ##        p = build_project()
            ##        projectset[project][placements].append(placement['company']['name'])
            pass
        validated_placement[field] = placement['company'][field]
    return validated_placement

def build_placement(validated_placement):
    placement = Placement(
        company_name=validated_placement['name'],
        job_title=validated_placement['job_title'],
        start_date=validated_placement['start_date'],
        end_date=validated_placement.get('end_date'),
        project_references=validated_placement['related_projects'] if 'related_projects' in validated_placement else None,
        reference_contacts=validated_placement['reference_contacts'] if 'reference_contacts' in validated_placement else None,
        related_skills=validated_placement['related_skills'] if 'related_skills' in validated_placement else None,
        reason_for_leaving=validated_placement['reason_for_leaving'] if 'reason_for_leaving' in validated_placement else None,
    )
    return placement
#endregion

#region skills tools
def parse_skills(file_path):
    skills = []
    file_data = read_yaml_file(file_path)
    for skill in file_data:
        print(f"Skill Name: {skill['skill']['skill_name']}")
        validated_skill = validate_skill_data(skill)
        finished_skill = build_skill(validated_skill)
        skills.append(finished_skill)
    return skills

def validate_skill_data(skill):
    validated_skill = {}
    required_fields = ['name']
    skill = skill['skill'] 
    for field in skill:
        if field in required_fields:
            if not skill[field]:
                raise ValueError(f"No {field} in skill")
        if field == "enjoyment_level":
            if not isinstance(skill[field], int) or skill[field] < 1 or skill[field] > 10:
                raise ValueError("Enjoyment level must be an integer between 1 and 10")
        validated_skill[field] = skill[field]
    return validated_skill

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
def parse_projects(file_path):
    projects = []
    file_data = read_yaml_file(file_path)
    for project in file_data:
        print(f"Project Name: {project['project_name']}")
        validated_project = validate_data(project, dataclass_type.PROJECT)
        finished_project = build_project(validated_project)
        projects.append(finished_project)
    return projects

def build_project(validated_project):
    project = Project(
        project_name=validated_project['project_name'],
        description=validated_project['description'],
        start_date=validated_project['start_date'] if 'start_date' in validated_project else None,
        end_date=validated_project['end_date'] if 'end_date' in validated_project else None,
        related_skills=validated_project['related_skills'] if 'related_skills' in validated_project else None,
        comment=validated_project['comment'] if 'comment' in validated_project else None,
    )
    return project
#endregion

#region hobby tools
def parse_hobbies(file_path):
    data_type = dataclass_type.HOBBY
    data = []
    finished_data = None
    file_data = read_yaml_file(file_path)
    for entry in file_data:
        print(f"{data_type.value} Name: {entry}")
        validated_data = validate_data(entry, data_type)
        finished_data = build_hobby(validated_data)
        data.append(finished_data)
    if not finished_data:
         raise ValueError(f"No valid {data_type.value} entries found in file")
    return finished_data
def build_hobby(validated_hobby):
    hobby = Hobby(
        hobby_name=validated_hobby['hobby_name'],
        description=validated_hobby['description'],
        related_skills=validated_hobby['related_skills'],
        tags=validated_hobby['tags'] if 'tags' in validated_hobby else None,
        awards_or_acolades=validated_hobby['awards_or_acolades'] if 'awards_or_acolades' in validated_hobby else None,
        comment=validated_hobby['comment'] if 'comment' in validated_hobby else None,
    )
    return hobby
#endregion

#region qualification tools
def parse_qualifications(file_path):
    return parse_data(file_path, dataclass_type.QUALIFICATION)
    
def build_qualification(validated_qualification):
    qualification = Qualification(
        qualification_name=validated_qualification['qualification_name'],
        studied_at=validated_qualification['studied_at'],
        awarded_date=validated_qualification['awarded_date'],
        grade = validated_qualification['grade'],
        related_skills=validated_qualification['related_skills'],
        tags=validated_qualification['tags'] if 'tags' in validated_qualification else [],
        expiration_date=validated_qualification['expiration_date'] if 'expiration_date' in validated_qualification else None,
        comment=validated_qualification['comment'] if 'comment' in validated_qualification else None,
    )
    return qualification
#endregion

#region people tools
def parse_people(file_path):
    return parse_data(file_path, dataclass_type.PERSON)

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

parse_placements("data/CV_Resources/Personal/placements.yaml")
parse_skills("data/CV_Resources/Personal/skills.yaml")
parse_projects("data/CV_Resources/Personal/projects.yaml")
parse_hobbies("data/CV_Resources/AI_Example_data/hobbies.yaml")
parse_qualifications("data/CV_Resources/AI_Example_data/qualifications.yaml")
parse_people("data/CV_Resources/AI_Example_data/people.yaml")