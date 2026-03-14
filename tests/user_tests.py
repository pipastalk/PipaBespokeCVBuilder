import logging
logging.disable(logging.CRITICAL)
import unittest
from datetime import date
from src.models.User import User
from src.models.data_ingestion import dataclass_type
from src.models.schema import *

	
class Test_User(unittest.TestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		self.test_values = {
			"name" : "Test User",
			"email": "notAnEmail@email.com", 
			"phone_number": "1234567890",
			"linkedin": "https://www.linkedin.com/in/testuser", 
			"github": "https://github.com/testuser",
			'skill' : Skill(
				cai_hash="10987654321skill",
				id="python-SKILL",
				name="Python",
				proficiency_level=None,
				enjoyment_level=None,
				tags=set(),
				related_placements=set(),
				related_projects=set(),
				related_qualifications=set()
			),
			'qualification' : Qualification(
				cai_hash="10987654321qual",
				id="bsc_computer_science-QUALIFICATION",
				name="BSc Computer Science",
				studied_at="University of Test",
				awarded_date=date(2020, 6, 1),
				grade="First Class",
				related_skills=set(),
				tags=set(),
				expiration_date=None,
				comment=None	
			),
			'project' : Project(
				cai_hash="10987654321proj",
				id="test_project_1098-PROJECT",
				name="Test Project",
				description="A project for testing",
				start_date=None,
				end_date=None,
				related_skills=set(),
				comment=None
			),
			'placement' : Placement(
				cai_hash="10987654321pla",
				id="test_company_software_engineer-PLACEMENT",
				name="Test Company",
				job_title="Software Engineer",
				start_date=date(2020, 1, 1),
				end_date=date(2020, 12, 31),
				project_references=set(),
				reference_contacts=set(),
				related_skills=set(),
				reason_for_leaving=None
			),
			'hobby' : Hobby(
				cai_hash="10987654321hob",
				id="testing-HOBBY",
				name="Testing",
				description="Testing things for fun",
				related_skills=set(),
				tags=set(),
				awards_or_accolades=set(),
				comment=None
			)
}
		super().__init__(methodName)
		
	def print_start(self, msg):
		starting = "----------------------STARTING----------------------"
		line_break = "___________________________________________________"
		print(f"\n{starting}\n{msg}\n{line_break}")
	
	def print_end(self, msg):
		line_break = "___________________________________________________"
		ending = "--------------------------ENDED-----------------------"
		print(f"\n{line_break}\n{msg}\n{ending}")

	def build_user_min_requirements(self):
		msg = "Testing build_user_min_requirements"
		self.print_start(msg)
		user = User(name=self.test_values['name'])
		value_is_name_checks = [user.person.name]
		value_is_dict_checks = [user.qualifications, user.projects, user.placements, user.hobbies, user.people]
		self.assertIsInstance(user.person, Person, "User.person should be an instance of Person dataclass")
		self.assertIsInstance(user.person.contact_details, ContactDetails, "User.person.contact_details should be an instance of ContactDetails dataclass")
		for value in value_is_dict_checks:
			self.assertIsInstance(value, dict, f"User's data collections should be a dictionary butn found type {type(value)}")
		
		for value in value_is_name_checks:
			self.assertEqual(value, self.test_values['name'], f"User's name has not been stored in the object correctly")
		
		self.print_end(msg)	

	def build_user_all_fields(self):
		pass

	def build_bad_user(self):
		msg = "Testing build_bad_user"
		self.print_start(msg)
		with self.assertRaises(ValueError):
			user = User(name=None) # type: ignore
		with self.assertRaises(ValueError):
			user = User(name="")
		with self.assertRaises(ValueError):
			user = User(name=1) # type: ignore
		with self.assertRaises(ValueError):
			user = User(name=["nested_string"]) # type: ignore
		self.print_end(msg)
	
	def test_generate_id(self):
		msg = "Build test_generate_id"
		self.print_start(msg)
		# expected_id should be manually set to the passed in dict, not within this function
		#(test_data, type, expected id,)
		#cai_hash, name, job_title
		user = User(name=self.test_values['name'])
		test_data = {
			'name': "Generic Testing Value",
			'cai_hash': "10987654321",
			'job_title': "Test Job Title"
		}
		#TODO add test cases for duplicate names
		expected_results = [ 
			(dataclass_type.SKILL, "generic_testing_value-SKILL"), #expected name-TYPE
			(dataclass_type.QUALIFICATION, "generic_testing_value-QUALIFICATION"), #expected name-TYPE
			(dataclass_type.PERSON, "10987654321-PERSON"), #expected cai_hash-TYPE
			(dataclass_type.PROJECT, "generic_testing_value-1098-PROJECT"),#expected name-shortHash-TYPE
			(dataclass_type.PLACEMENT, "generic_testing_value-test_job_title-PLACEMENT"), #expected name-jobTitle-TYPE
			(dataclass_type.HOBBY, "generic_testing_value-HOBBY"), #expected name-TYPE
		]
		for d_type, expected_id in expected_results:
			result = user.generate_id(data=test_data, d_type=d_type)
			self.assertEqual(result, expected_id, f"Failed to generate accurate expected_id. \n {d_type.value} name: {test_data['name']}\n generated_result: {result}\n expected result: {expected_id}")
		self.print_end(msg)

	def test_add_data(self):
		msg = "Testing test_add_data"
		self.print_start(msg)
		#data, type. target
		user = User(name=self.test_values['name'])
		expected_results = [
			(self.test_values['skill'], dataclass_type.SKILL, user.skills),
			(self.test_values['qualification'], dataclass_type.QUALIFICATION, user.qualifications),
			#TODO (self.test_values['person'], dataclass_type.PERSON, user.people),
			(self.test_values['project'], dataclass_type.PROJECT, user.projects),
			(self.test_values['placement'], dataclass_type.PLACEMENT, user.placements),
			(self.test_values['hobby'], dataclass_type.HOBBY, user.hobbies)
		]
			
		for data, d_type, tar_dict in expected_results:
			user.add_data(data, d_type)
			self.assertIs(tar_dict[data.id], data, f"Failed to add {d_type.value} to user")
		self.print_end(msg)

	def test_get_dict(self):
		msg = "Testing test_get_dict"
		self.print_start(msg)
		user = User(name=self.test_values['name'])
		expected_results = [
			(dataclass_type.SKILL, user.skills),
			(dataclass_type.QUALIFICATION, user.qualifications),
			(dataclass_type.PERSON, user.people),
			(dataclass_type.PROJECT, user.projects),
			(dataclass_type.PLACEMENT, user.placements),
			(dataclass_type.HOBBY, user.hobbies),
		]
		for d_type, tar_dict in expected_results:
			result = user.get_dict(d_type)
			self.assertIs(result, tar_dict, f"Failed to get correct dict for {d_type.value}")
		self.print_end(msg)

	def test_get_item(self):
		msg = "Testing test_get_item"
		self.print_start(msg)
		user = User(name=self.test_values['name'])
		expected_results = [
			(self.test_values['skill'].id, dataclass_type.SKILL, user.skills,self.test_values['skill']),
			(self.test_values['qualification'].id, dataclass_type.QUALIFICATION, user.qualifications,self.test_values['qualification']),
			#(self.test_values['person'].id, dataclass_type.PERSON, user.people,self.test_values['person']),
			(self.test_values['project'].id, dataclass_type.PROJECT, user.projects,self.test_values['project']),
			(self.test_values['placement'].id, dataclass_type.PLACEMENT, user.placements,self.test_values['placement']),
			(self.test_values['hobby'].id, dataclass_type.HOBBY, user.hobbies,self.test_values['hobby']),
		]
		for data, d_type, tar_dict, expected_result in expected_results:
			tar_dict[data] = expected_result #manual add of item
			result = user.get_item(data, d_type)
			self.assertIs(result, expected_result, f"Failed to get correct item for {d_type.value} with id {data}")
		self.print_end(msg)

	def test_hash_search(self):
		msg = "Test test_hash_search"
		self.print_start(msg)
		#search_data, expected_results(object, object_type)
		expected_results = [
			(self.test_values['skill'].cai_hash, (self.test_values['skill'], dataclass_type.SKILL)),
			(self.test_values['qualification'].cai_hash, (self.test_values['qualification'], dataclass_type.QUALIFICATION)),
			#self.test_values['person'].cai_hash, (self.test_values['person'], dataclass_type.PERSON)),
			(self.test_values['project'].cai_hash, (self.test_values['project'], dataclass_type.PROJECT)),
			(self.test_values['placement'].cai_hash, (self.test_values['placement'], dataclass_type.PLACEMENT)),
			(self.test_values['hobby'].cai_hash, (self.test_values['hobby'], dataclass_type.HOBBY))
		]
		user = User(name=self.test_values['name'])
		user.skills[self.test_values['skill'].id] = self.test_values['skill']
		user.qualifications[self.test_values['qualification'].id] = self.test_values['qualification']
		#user.people[self.test_values['person'].id] = self.test_values['person']
		user.projects[self.test_values['project'].id] = self.test_values['project']
		user.placements[self.test_values['placement'].id] = self.test_values['placement']
		user.hobbies[self.test_values['hobby'].id] = self.test_values['hobby']
		
		for search_data, expected_result in expected_results:
			result = user.hash_search(search_data)
			self.assertIsNotNone(result, "Failed to find item with cai_hash search")
			self.assertEqual(result, expected_result, f"search by cai hash failed to retrieve right item\nresult: NAME-{result[0].name} TYPE-{result[1]}\nexpected_result: NAME-{expected_result[0].name}, TYPE-{expected_result[1]}\nsearch data:{search_data}") 
		self.print_end(msg)

	def test_set_link_skill_to_item(self):
		msg = "Testing test_set_link_skill_to_item"
		self.print_start(msg)
		#target_data, skill_to_link, item_type
		expected_results = [
			(self.test_values['project'].id, self.test_values['skill'].id, dataclass_type.PROJECT),
			(self.test_values['placement'].id, self.test_values['skill'].id, dataclass_type.PLACEMENT),
			(self.test_values['qualification'].id, self.test_values['skill'].id, dataclass_type.QUALIFICATION),
			(self.test_values['hobby'].id, self.test_values['skill'].id, dataclass_type.HOBBY)
		]
		user = User(name=self.test_values['name'])
		user.skills[self.test_values['skill'].id] = self.test_values['skill']
		user.qualifications[self.test_values['qualification'].id] = self.test_values['qualification']
		#user.people[self.test_values['person'].id] = self.test_values['person']
		user.projects[self.test_values['project'].id] = self.test_values['project']
		user.placements[self.test_values['placement'].id] = self.test_values['placement']
		user.hobbies[self.test_values['hobby'].id] = self.test_values['hobby']
		for target_data, skill_to_link, item_type in expected_results:
			user.set_link_skill_to_item(target_data, skill_to_link, item_type)
			item = user.get_item(target_data, item_type)
			self.assertIsNotNone(item, f"Failed to find {item_type.value} with id {target_data} when trying to link skill")
			self.assertIn(skill_to_link, item.related_skills, f"Failed to link skill {skill_to_link} to {item_type.value} with id {target_data}") # type: ignore
		#TODO add test cases for already linked skill, non existent skill, non existent item
		self.print_end(msg)


if __name__ == '__main__':
    
    unittest.main()

