from schema import *
class User:
    def __init__(self, name: str, email = None, phone_number = None, linkedin = None, github = None, other_links = None):
        email = email if email else None
        phone_number = phone_number if phone_number else None
        linkedin = linkedin if linkedin else None
        github = github if github else None
        other_links = other_links if other_links else None
        contact_details = ContactDetails(name=name, email=email, phone_number=phone_number, linkedin=linkedin, github=github, other_links=other_links) #TODO 
        self.skills = []
        self.qualifications = []
        self.person = Person(name=name, relation_type="USER", is_reference=False, contact_details=contact_details, comment=None) #TODO
        self.projects = []
        self.placements = []
        self.hobbies = []
        self.people = []