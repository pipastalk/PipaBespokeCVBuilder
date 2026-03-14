from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

@dataclass
class Skill:
    skill_name: str
    id: str
    cai_hash: str
    proficiency_level: Optional[str]
    enjoyment_level: Optional[int] # how much do I enjoy this skill, could do with better name
    tags: set[str] = field(default_factory=set)
    related_placements: Optional[dict[str, "Placement"]]
    related_projects: Optional[dict[str, "Project"]]
    related_qualifications: Optional[dict[str, "Qualification"]]
@dataclass
class Qualification:
    id: str
    qualification_name: str
    studied_at: str
    awarded_date: datetime
    cai_hash: str
    related_skills: dict[str,"Skill"]
    tags: set[str] = field(default_factory=set)
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
    cai_hash: str
    id: str
    name: str
    relation_type: str
    is_reference: bool
    contact_details: Optional[ContactDetails]
    comment: Optional[str]
@dataclass
class Project:
    id: str
    project_name: str
    description: str
    cai_hash: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    related_skills: Optional[dict[str, "Skill"]]
    comment: Optional[str]
@dataclass
class Placement:
    id: str
    company_name: str
    job_title: str
    start_date: date
    cai_hash: str
    end_date: date
    reason_for_leaving: Optional[str]
    project_references: set[str] = field(default_factory=set)
    reference_contacts: set[str] = field(default_factory=set)
    related_skills: set[str] = field(default_factory=set)
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
    id: str
    hobby_name: str
    description: str
    cai_hash: str
    related_skills: Optional[dict[str, "Skill"]]
    tags: set[str] = field(default_factory=set)
    awards_or_accolades: Optional[list[str]]
    comment: Optional[str]