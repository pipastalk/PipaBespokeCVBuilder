from schema import *
class User:
    def __init__(self, name: str, email = None, phone_number = None, linkedin = None, github = None, other_links = None):
        contact_details = ContactDetails(name=name, email=email, phone_number=phone_number, linkedin=linkedin, github=github, other_links=other_links) #TODO 
        self.skills = {}
        self.qualifications = {}
        self.person = Person(name=name, cai_hash="USER.PRIMARY", id="USER.PRIMARY", relation_type="USER", is_reference=False, contact_details=contact_details, comment=None) #TODO
        self.projects = {}
        self.placements = {}
        self.hobbies = {}
        self.people = {}