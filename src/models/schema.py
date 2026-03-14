from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

@dataclass
class Skill:
    name: str
    id: str
    cai_hash: str
    proficiency_level: Optional[str]
    enjoyment_level: Optional[int] # how much do I enjoy this skill, could do with better name
    tags: set[str] = field(default_factory=set)
    related_placements: set[str] = field(default_factory=set)
    related_projects: set[str] = field(default_factory=set)
    related_qualifications: set[str] = field(default_factory=set)
@dataclass
class Qualification:
    id: str
    name: str
    studied_at: str
    awarded_date: date
    cai_hash: str
    grade: Optional[str]
    expiration_date: Optional[date] # for qualifications that expire, e.g. first aid, cpr, etc.
    comment: Optional[str]
    related_skills: set[str] = field(default_factory=set)
    tags: set[str] = field(default_factory=set)
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
    name: str
    description: str
    cai_hash: str
    start_date: Optional[date]
    end_date: Optional[date]
    comment: Optional[str]
    related_skills: set[str] = field(default_factory=set)
@dataclass
class Placement:
    id: str
    name: str
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
    name: str
    description: str
    cai_hash: str
    comment: Optional[str]
    tags: set[str] = field(default_factory=set)
    awards_or_accolades: set[str] = field(default_factory=set)
    related_skills: set[str] = field(default_factory=set)
    