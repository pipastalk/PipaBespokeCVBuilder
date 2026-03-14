import unittest
from models.schema import * 
from src.models.User import User
from src.models.data_ingestion import *

test_values = {
    "name" : "Test User",
    "email": "notAnEmail@email.com", 
    "phone_number": "1234567890",
	"linkedin": "https://www.linkedin.com/in/testuser", 
    "github": "https://github.com/testuser",
	'skill' : build_skill("Python", "Programming language", "Expert"),
	'qualification' : build_qualification("BSc Computer Science", "University of Test", "2010-2014"),
	'project' : build_project("Test Project", "A project for testing", "2020-01-01", "2020-12-31"),
	'placement' : build_placement("Test Company", "Software Engineer", "2020-01-01", "2020-12-31"),
	'hobby' : build_hobby("Testing", "Testing things for fun")
}

class Test_User(unittest.TestCase):

	def build_user_min_requirements(self, test_values):
		user = User(name=test_values['name'])
		value_is_name_checks = [user.person.name, user.contact_details.name]
		value_is_dict_checks = [user.skills, user.qualifications, user.projects, user.placements, user.hobbies, user.people]
		self.assertIsInstance(user.contact_details, ContactDetails)
		self.assertIsInstance(user.person, Person)
		for value in value_is_dict_checks:{
			self.assertIsInstance(value, dict)
		}
		for value in value_is_name_checks:{
			self.assertEqual(value, test_values['name'])
		}
	
	def build_user_all_fields(self, test_values):
		pass

	def build_bad_user(self, test_values):
		with self.assertRaises(ValueError):
			user = User(name=None)
		with self.assertRaises(ValueError):
			user = User(name="")
		with self.assertRaises(ValueError):
			user = User(name=1)
		with self.assertRaises(ValueError):
			user = User(name=["nested_string"])
	
	def test_generate_id(self, test_values):
		expected_results = [
			(test_values['skill'], "python-SKILL"),
			(test_values['qualification'], "bsc_computer_science-QUALIFICATION"),
			(test_values['person'], test_values['person'].cai_hash),
			(test_values['project'], ""),
			(test_values['placement'], "TODO"),
			(test_values['hobby'], "TODO")
		]

	def test_hash_search(self):
		pass

	def test_add_data(self,test_values):
		user = User(name=test_values['name'])
		user.add_data(skill, dataclass_type.SKILL)
	
	def test_get_dict(self):
		pass

	def test_get_item(self):
		pass

	def test_set_link_skill_to_item(self):
		pass

	def test__validate_link_data(self):
		pass


