import pytest
import unittest
from unittest.mock import MagicMock

from src.models.data_ingestion import *
from src.models.schema import *

class TestDataIngestion(unittest.TestCase):
    def test_build_contact_details(self):
        #region Minimum fields
        min_name = "John Doe"
        expected_min_contact_details = ContactDetails(
            name=min_name
        )
        example_data_min = {
            "name": min_name
        }
        
        #region Maximum fields
        max_name = "Michael Smith"
        max_email = "michael.smith@example.com"
        max_phone_number = "123-456-7890"
        max_linkedin = "https://www.linkedin.com/in/michaelsmith"
        max_github = "https://github.com/michaelsmith"
        max_other_links = ["https://www.michaelsmith.com", "https://www.michaelsmithblog.com"]
        expected_max_contact_details = ContactDetails(
            name=max_name,
            email=max_email,
            phone_number=max_phone_number,
            linkedin=max_linkedin,
            github=max_github,
            other_links=max_other_links
        )
        example_data_max = {
            "name": max_name,
            "email": max_email,
            "phone_number": max_phone_number,
            "linkedin": max_linkedin,
            "github": max_github,
            "other_links": max_other_links
        }
        #endregion

        #region Tests
        example_contact = build_contact_details(example_data_min)
        self.assertEqual(example_contact, expected_min_contact_details, "Failed to build Contact Details with minimum details")
        example_contact = build_contact_details(example_data_max)
        self.assertEqual(example_contact, expected_max_contact_details, "Failed to build Contact Details with all details") 
        #endregion
    
    def test_build_person(self):
        #region Minimum fields
        min_cai_hash = "abc123"
        min_id = "person1"
        min_name = "John Doe"
        min_relation_type = "friend"
        min_is_reference = False
        expected_min_person = Person(
            cai_hash=min_cai_hash,
            id=min_id,
            name=min_name,
            relation_type=min_relation_type,
            is_reference=min_is_reference
        )
        example_data_min = {
            "cai_hash": min_cai_hash,
            "id": min_id,
            "name": min_name,
            "relation_type": min_relation_type,
            "is_reference": min_is_reference
        }
        #endregion
        
        #region Maximum fields
        max_cai_hash = "def456"
        max_id = "person2"
        max_name = "Michael Smith"
        max_relation_type = "colleague"
        max_is_reference = True
        max_email = "michael.smith@example.com"
        max_phone_number = "987-654-3210"
        max_linkedin = "https://www.linkedin.com/in/michaelsmith"
        max_github = "https://github.com/michaelsmith"
        max_other_links = ["https://www.michaelsmith.com", "https://www.michaelsmithblog.com"]
        expected_max_person = Person(
            cai_hash=max_cai_hash,
            id=max_id,
            name=max_name,
            relation_type=max_relation_type,
            is_reference=max_is_reference,
            contact_details=ContactDetails(
                name=max_name,
                email=max_email,
                phone_number=max_phone_number,
                linkedin=max_linkedin,
                github=max_github,
                other_links=max_other_links
            )
        )
        example_data_max = {
            "cai_hash": max_cai_hash,
            "id": max_id,
            "name": max_name,
            "relation_type": max_relation_type,
            "is_reference": max_is_reference,
            "contact_details": {
                "name": max_name,
                "email": max_email,
                "phone_number": max_phone_number,
                "linkedin": max_linkedin,
                "github": max_github,
                "other_links": max_other_links
            }
        }   
        #endregion

        #region Tests
        user = User("Test User")
        example_person = build_person(example_data_min, user)
        self.assertEqual(example_person, expected_min_person, "Failed to build Person with minimum details")
        example_person = build_person(example_data_max, user)
        self.assertEqual(example_person, expected_max_person, "Failed to build Person with all details")
        #endregion

    def test_build_qualification(self):

        #region Minimum Requirements
        min_id = "qual1"
        min_name = "Bachelor's Degree"
        min_studied_at = "University of Example"
        min_awarded_date = "2020-06-01"
        min_cai_hash = "qualhash123"
        expected_min_qualification = Qualification(
            id=min_id,
            name=min_name,
            studied_at=min_studied_at,
            awarded_date=datetime.strptime(min_awarded_date, "%Y-%m-%d").date(),
            cai_hash=min_cai_hash
        )
        example_data_min = {
            "id": min_id,
            "name": min_name,
            "studied_at": min_studied_at,
            "awarded_date": min_awarded_date,
            "cai_hash": min_cai_hash
        }
        #endregion

        #region Maximum fields
        max_id = "qual2"
        max_name = "Master's Degree"
        max_studied_at = "Example University"
        max_awarded_date = "2022-05-15"
        max_cai_hash = "qualhash456"
        max_grade = "A"
        max_expiration_date = "2030-05-15"
        max_comment = "Graduated with honors."
        related_skills = {"Research", "Data Analysis"}
        tags = {"Education", "Higher Education"}
        expected_max_qualification = Qualification(
            id=max_id,
            name=max_name,
            studied_at=max_studied_at,
            awarded_date=datetime.strptime(max_awarded_date, "%Y-%m-%d").date(),
            cai_hash=max_cai_hash,
            grade=max_grade,
            expiration_date=datetime.strptime(max_expiration_date, "%Y-%m-%d").date(),
            comment=max_comment,
            related_skills=related_skills,
            tags=tags
        )
        example_data_max = {
            "id": max_id,
            "name": max_name,
            "studied_at": max_studied_at,
            "awarded_date": max_awarded_date,
            "cai_hash": max_cai_hash,
            "grade": max_grade,
            "expiration_date": max_expiration_date,
            "comment": max_comment,
            "related_skills": list(related_skills),
            "tags": list(tags)
        }   
        #endregion 

        #region Test
        user = User("Test User")
        example_qualification = build_qualification(example_data_min, user)
        self.assertEqual(example_qualification, expected_min_qualification, "Failed to build Qualification with minimum details")
        example_qualification = build_qualification(example_data_max, user)
        self.assertEqual(example_qualification, expected_max_qualification, "Failed to build Qualification with all details")
        #endregion

    def test_build_hobby(self):
        #region Minimum fields
        min_name = "Photography"
        min_id = "hobby1"
        min_cai_hash = "hobbyhash123"
        min_description = "I point a camera at things yo"
        expected_min_hobby = Hobby(
            name=min_name,
            id=min_id,
            cai_hash=min_cai_hash,
            description=min_description
        )
        example_data_min = {
            "name": min_name,
            "id": min_id,
            "cai_hash": min_cai_hash,
            "description": min_description
        }
        #endregion

        #region Maximum fields
        max_name = "Traveling"
        max_id = "hobby2"
        max_description = "Exploring new places and cultures around the world."
        max_cai_hash = "hobbyhash123"
        max_comment = "I have visited over 30 countries and counting!"
        max_tags = {"Adventure", "Culture", "Food"}
        max_awards_or_accolades = {"Best Travel Blogger 2023", "Top 10 Travel Influencers 2022"}    
        max_related_skills = {"Cultural Awareness", "Language Skills", "Photography"}
        expected_max_hobby = Hobby(
            name=max_name,
            description=max_description,
            cai_hash=max_cai_hash,
            comment=max_comment,
            tags=max_tags,
            awards_or_accolades=max_awards_or_accolades,
            related_skills=max_related_skills,
            id=max_id
        )
        example_data_max = {
            "name": max_name,
            "description": max_description,
            "cai_hash": max_cai_hash,
            "comment": max_comment,
            "tags": list(max_tags),
            "awards_or_accolades": list(max_awards_or_accolades),
            "related_skills": list(max_related_skills),
            "id": max_id
        }
        #endregion

        #region Tests
        example_hobby = build_hobby(example_data_min)
        self.assertEqual(example_hobby, expected_min_hobby, "Failed to build Hobby with minimum details")
        example_hobby = build_hobby(example_data_max)
        self.assertEqual(example_hobby, expected_max_hobby, "Failed to build Hobby with all details") 
        #endregion

    def test_build_project(self):
        #region Minimum fields
        min_id = "project1"
        min_name = "Personal Website"
        min_description = "A simple personal website built with HTML, CSS, and JavaScript."
        min_cai_hash = "projecthash123"
        expected_min_project = Project(
            id=min_id,
            name=min_name,
            description=min_description,
            cai_hash=min_cai_hash
        )
        example_data_min = {
            "id": min_id,
            "name": min_name,
            "description": min_description,
            "cai_hash": min_cai_hash
        }
        #endregion

        #region Maximum fields
        max_cai_hash = "projecthash456"
        max_id = "project2"
        max_name = "E-commerce Platform"
        max_description = "A full-featured e-commerce platform built with Django and React."
        max_start_date = "2021-01-01"
        max_end_date = "2021-12-31"
        max_related_skills = {"Web Development", "Django", "React", "JavaScript"}
        max_comment = "This project was a major milestone in my career and received positive feedback from users."
        expected_max_project = Project(
            id=max_id,
            name=max_name,
            description=max_description,
            cai_hash=max_cai_hash,
            start_date=datetime.strptime(max_start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(max_end_date, "%Y-%m-%d").date(),
            related_skills=max_related_skills,
            comment=max_comment
        )
        example_data_max = {
            "id": max_id,
            "name": max_name,
            "description": max_description,
            "cai_hash": max_cai_hash,
            "start_date": max_start_date,
            "end_date": max_end_date,
            "related_skills": list(max_related_skills),
            "comment": max_comment
        }
        #endregion

        #region Tests
        example_project = build_project(example_data_min)
        self.assertEqual(example_project, expected_min_project, "Failed to build Project with minimum details")
        example_project = build_project(example_data_max)
        self.assertEqual(example_project, expected_max_project, "Failed to build Project with all details")
        #endregion

    def test_build_skill(self):
        #region Minimum fields
        min_id = "skill1"
        min_name = "Python"
        min_cai_hash = "skillhash123"
        expected_min_skill = Skill(
            id=min_id,
            name=min_name,
            cai_hash=min_cai_hash
        )
        example_data_min = {
            "id": min_id,
            "name": min_name,
            "cai_hash": min_cai_hash
        }
        #endregion

        #region Maximum fields
        max_id = "skill2"
        max_name = "Software Engineering"
        max_cai_hash = "skillhash456"
        max_proficiency_level = "Advanced"
        max_enjoyment_level = 9
        max_tags = {"Backend", "Architecture", "Testing"}
        max_related_placements = {"placement1", "placement2"}
        max_related_projects = {"project1", "project2"}
        max_related_qualifications = {"qual1", "qual2"}
        expected_max_skill = Skill(
            id=max_id,
            name=max_name,
            cai_hash=max_cai_hash,
            proficiency_level=max_proficiency_level,
            enjoyment_level=max_enjoyment_level,
            tags=max_tags,
            related_placements=max_related_placements,
            related_projects=max_related_projects,
            related_qualifications=max_related_qualifications
        )
        example_data_max = {
            "id": max_id,
            "name": max_name,
            "cai_hash": max_cai_hash,
            "proficiency_level": max_proficiency_level,
            "enjoyment_level": max_enjoyment_level,
            "tags": max_tags,
            "related_placements": max_related_placements,
            "related_projects": max_related_projects,
            "related_qualifications": max_related_qualifications
        }
        #endregion

        #region Tests
        example_skill = build_skill(example_data_min)
        self.assertEqual(example_skill, expected_min_skill, "Failed to build Skill with minimum details")
        example_skill = build_skill(example_data_max)
        self.assertEqual(example_skill, expected_max_skill, "Failed to build Skill with all details")
        #endregion

    def test_build_placement(self):
        #region Minimum fields
        min_id = "placement1"
        min_name = "Example Corp"
        min_job_title = "Junior Developer"
        min_start_date = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
        min_end_date = datetime.strptime("2023-01-01", "%Y-%m-%d").date()
        min_cai_hash = "placementhash123"
        expected_min_placement = Placement(
            id=min_id,
            name=min_name,
            job_title=min_job_title,
            start_date=min_start_date,
            end_date=min_end_date,
            cai_hash=min_cai_hash
        )
        example_data_min = {
            "id": min_id,
            "name": min_name,
            "job_title": min_job_title,
            "start_date": min_start_date,
            "end_date": min_end_date,
            "cai_hash": min_cai_hash
        }
        #endregion

        #region Maximum fields
        max_id = "placement2"
        max_name = "Tech Solutions Ltd"
        max_job_title = "Senior Engineer"
        max_start_date = datetime.strptime("2023-02-01", "%Y-%m-%d").date()
        max_end_date = datetime.strptime("2025-02-01", "%Y-%m-%d").date()
        max_cai_hash = "placementhash456"
        max_reason_for_leaving = "Pursued a new leadership opportunity"
        max_project_references = {"project1", "project2"}
        max_reference_contacts = {"person1", "person2"}
        max_related_skills = {"skill1", "skill2"}
        expected_max_placement = Placement(
            id=max_id,
            name=max_name,
            job_title=max_job_title,
            start_date=max_start_date,
            end_date=max_end_date,
            cai_hash=max_cai_hash,
            reason_for_leaving=max_reason_for_leaving,
            project_references=max_project_references,
            reference_contacts=max_reference_contacts,
            related_skills=max_related_skills
        )
        example_data_max = {
            "id": max_id,
            "name": max_name,
            "job_title": max_job_title,
            "start_date": max_start_date,
            "end_date": max_end_date,
            "cai_hash": max_cai_hash,
            "reason_for_leaving": max_reason_for_leaving,
            "related_projects": max_project_references,
            "reference_contacts": max_reference_contacts,
            "related_skills": max_related_skills
        }
        #endregion

        #region Tests
        example_placement = build_placement(example_data_min)
        self.assertEqual(example_placement, expected_min_placement, "Failed to build Placement with minimum details")
        example_placement = build_placement(example_data_max)
        self.assertEqual(example_placement, expected_max_placement, "Failed to build Placement with all details")
        #endregion

