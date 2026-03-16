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