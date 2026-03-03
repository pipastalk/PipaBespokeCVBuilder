from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass
class Company:
    company_name: str
    industry: str
    size: int
    culture: str
    comment: str # personal notes about the company
@dataclass
class Skill:
    skill_name: str
    proficiency_level: str
    related_placements: list["Placement"]
    related_projects: list["Project"]
    related_qualifications: list["Qualification"]
    enjoyment_level: int # how much do I enjoy this skill, could do with better name
    tags: list[str]
@dataclass
class Qualification:
    qualification_name: str
    studied_at: str 
    grade: str
    awarded_date: datetime
    expiration_date: datetime # for qualifications that expire, e.g. first aid, cpr, etc.
    related_skills: list["Skill"]
    comment: str
    tags: list[str]
@dataclass
class ContactDetails:
    email: str
    phone_number: str
    linkedin: str
    github: str
    other_links: list[str]
@dataclass
class Person:
    name: str
    contact_details: ContactDetails
    relation_type: str
    comment: str
    is_reference: bool
@dataclass
class Project:
    project_name: str
    description: str
    related_skills: list["Skill"]
    start_date: datetime
    end_date: datetime
    comment: str
@dataclass
class Placement:
    company_details: Company
    job_title: str
    start_date: datetime
    end_date: datetime
    project_references: list["Project"]
    reference_contacts: list["Person"]
    reason_for_leaving: str
    related_skills: list["Skill"]
@dataclass
class Location:
    address: str #is there a library for this?
    city: str
    country: str #maybe use ISO country codes and a enum for this?
    post_or_zip_code: str #check libraries for validating this?
    gps_coordinates: str #TODO bonus extra for google maps link
@dataclass
class AdvertSource:
    source_path: str #url or file path
    sourced_from: str #where this advert was found, e.g. linkedin, company website, etc.
    comment: str #personal notes about the advert
@dataclass
class Advert:
    advert_title: str
    advert_description: str
    source: AdvertSource
    companyDetails: Company
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
    related_skills: list["Skill"]
    awards_or_acolades: list[str]
    tags: list[str]
    comment: str