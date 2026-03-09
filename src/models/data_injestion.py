import os
import yaml
from enum import Enum
from datetime import datetime
from schema import *

#region generic tools
class dataclass_type(Enum):
    SKILL = "Skill"
    PROJECT = "Project"
    PLACEMENT = "Placement"

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
        case dataclass_type.SKILL:
            working_data = data['skill']
            required_fields = ['skill_name']
        case dataclass_type.PROJECT:
            working_data = data
            required_fields = ['name', 'description']
        case dataclass_type.PLACEMENT:
            working_data = data['company']
            required_fields = ['name', 'start_date', 'job_title', 'related_skills']
        case _:
            raise ValueError("Invalid dataclass type provided for validation")

    if not working_data:
        raise ValueError("Placement was invalid, expected company as base field")
    for field in working_data:
        if field in required_fields:
            if not working_data[field]:
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

parse_placements("data/CV_Resources/Personal/placements.yaml")
parse_skills("data/CV_Resources/Personal/skills.yaml")
parse_projects("data/CV_Resources/Personal/projects.yaml")