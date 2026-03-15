import pytest
import unittest
from unittest.mock import MagicMock

from src.models.data_ingestion import *
from src.models.schema import *

class TestDataIngestion(unittest.TestCase):
    def test_build_contact_details(self):
        # Mocking the ContactDetails class

        #Minimum Requirements
        expected_min_contact_details = ContactDetails(
            name="John Doe"
        )
        example_data_min = {
            "name": "John Doe"
        }
        
        #All fields
        expected_max_contact_details = ContactDetails(
            name="Michael Smith",
            email="michael.smith@example.com",
            phone_number="123-456-7890",
            linkedin="https://www.linkedin.com/in/michaelsmith",
            github="https://github.com/michaelsmith",
            other_links=["https://www.michaelsmith.com", "https://www.michaelsmithblog.com"]
        )
        example_data_max = {
            "name": "Michael Smith",
            "email": "michael.smith@example.com",
            "phone_number": "123-456-7890",
            "linkedin": "https://www.linkedin.com/in/michaelsmith",
            "github": "https://github.com/michaelsmith",
            "other_links": ["https://www.michaelsmith.com", "https://www.michaelsmithblog.com"]
        }

        example_contact = build_contact_details(example_data_min)
        self.assertEqual(example_contact, expected_min_contact_details, "Failed to build Contact Details with minimum details")
        example_contact = build_contact_details(example_data_max)
        self.assertEqual(example_contact, expected_max_contact_details, "Failed to build Contact Details with all details") 

    def test_build_person(self):
        # Mocking the Person class

        #Minimum Requirements
        expected_min_person = Person(
            cai_hash="abc123",
            id="person1",
            name="John Doe",
            relation_type="friend",
            is_reference=False
        )
        example_data_min = {
            "cai_hash": "abc123",
            "id": "person1",
            "name": "John Doe",
            "relation_type": "friend",
            "is_reference": False
        }
        
        #All fields
        expected_max_person = Person(
            cai_hash="def456",
            id="person2",
            name="Michael Smith",
            relation_type="colleague",
            is_reference=True,
            contact_details=ContactDetails(
                name="Michael Smith",
                email="michael.smith@example.com",
                phone_number="987-654-3210",
                linkedin="https://www.linkedin.com/in/michaelsmith",
                github="https://github.com/michaelsmith",
                other_links=["https://www.michaelsmith.com", "https://www.michaelsmithblog.com"]
            )
        )
        example_data_max = {
            "cai_hash": "def456",
            "id": "person2",
            "name": "Michael Smith",
            "relation_type": "colleague",
            "is_reference": True,
            "contact_details": {
                "name": "Michael Smith",
                "email": "michael.smith@example.com",
                "phone_number": "987-654-3210",
                "linkedin": "https://www.linkedin.com/in/michaelsmith",
                "github": "https://github.com/michaelsmith",
                "other_links": ["https://www.michaelsmith.com", "https://www.michaelsmithblog.com"]
            }
        }   
        user = User("Test User")
        example_person = build_person(example_data_min, user)
        self.assertEqual(example_person, expected_min_person, "Failed to build Person with minimum details")
        example_person = build_person(example_data_max, user)
        self.assertEqual(example_person, expected_max_person, "Failed to build Person with all details")

    def test_build_qualification(self):
        # Mocking the Qualification class

        #Minimum Requirements
        expected_min_qualification = Qualification(
            id="qual1",
            name="Bachelor's Degree",
            studied_at="University of Example",
            awarded_date=date(2020, 6, 1),
            cai_hash="qualhash123"
        )
        example_data_min = {
            "id": "qual1",
            "name": "Bachelor's Degree",
            "studied_at": "University of Example",
            "awarded_date": "2020-06-01",
            "cai_hash": "qualhash123"
        }
        
        #All fields
        expected_max_qualification = Qualification(
            id="qual2",
            name="Master's Degree",
            studied_at="Example University",
            awarded_date=date(2022, 5, 15),
            cai_hash="qualhash456",
            grade="A",
            expiration_date=date(2030, 5, 15),
            comment="Graduated with honors.",
            related_skills={"Research", "Data Analysis"},
            tags={"Education", "Higher Education"}
        )
        example_data_max = {
            "id": "qual2",
            "name": "Master's Degree",
            "studied_at": "Example University",
            "awarded_date": "2022-05-15",
            "cai_hash": "qualhash456",
            "grade": "A",
            "expiration_date": "2030-05-15",
            "comment": "Graduated with honors.",
            "related_skills": ["Research", "Data Analysis"],
            "tags": ["Education", "Higher Education"]
        }   
        user = User("Test User")
        example_qualification = build_qualification(example_data_min, user)
        self.assertEqual(example_qualification, expected_min_qualification, "Failed to build Qualification with minimum details")
        example_qualification = build_qualification(example_data_max, user)
        self.assertEqual(example_qualification, expected_max_qualification, "Failed to build Qualification with all details")

#TODO build rest of these tests