from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

@dataclass
class Skill:
    skill_name: str
    proficiency_level: Optional[str]
    enjoyment_level: Optional[int] # how much do I enjoy this skill, could do with better name
    tags: Optional[list[str]]
    related_placements: Optional[list["Placement"]]
    related_projects: Optional[list["Project"]]
    related_qualifications: Optional[list["Qualification"]]
@dataclass
class Qualification:
    qualification_name: str
    studied_at: str
    awarded_date: datetime
    related_skills: list["Skill"]
    tags: Optional[list[str]]
    grade: Optional[str]
    expiration_date: Optional[datetime] # for qualifications that expire, e.g. first aid, cpr, etc.
    comment: Optional[str]
@dataclass
class ContactDetails:
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    other_links: Optional[list[str]]
@dataclass
class Person:
    name: str
    relation_type: str
    is_reference: bool
    contact_details: Optional[ContactDetails]
    comment: Optional[str]
@dataclass
class Project:
    project_name: str
    description: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    related_skills: Optional[list["Skill"]]
    comment: Optional[str]
@dataclass
class Placement:
    company_name: str
    job_title: str
    start_date: datetime
    end_date: Optional[datetime]
    project_references: Optional[list["Project"]]
    reference_contacts: Optional[list["Person"]]
    related_skills: Optional[list["Skill"]]
    reason_for_leaving: Optional[str]
@dataclass
class Location:
    city: str #Will accept Remote/Home as a city
    country: str #maybe use ISO country codes and a enum for this?
    address: Optional[str] #is there a library for this?
    post_or_zip_code: Optional[str] #check libraries for validating this?
    gps_coordinates: Optional[str] #TODO bonus extra for google maps link
@dataclass
class AdvertSource:
    source_path: str #url or file path
    sourced_from: str #where this advert was found, e.g. linkedin, company website, etc.
    comment: Optional[str] #personal notes about the advert
@dataclass
class Advert:
    advert_title: str
    advert_description: str
    source: AdvertSource
    required_skills: list["Skill"]
    desired_skills: list["Skill"]
    placement_location: Location
    working_pattern: str #maybe could enum this later, remote,hybrid,flex,shifts etc
    contact_details: ContactDetails
    advertStyle: Enum #e.g. formal, informal, creative, etc. 
@dataclass
class Hobby:
    hobby_name: str
    description: str
    related_skills: Optional[list["Skill"]]
    tags: Optional[list[str]]
    awards_or_accolades: Optional[list[str]]
    comment: Optional[str]