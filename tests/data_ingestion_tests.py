import pytest

from src.models.data_ingestion import *
from src.models.schema import *


@pytest.fixture
def basic_user():
    return User("Test User")


@pytest.mark.parametrize(
    "example_data, expected_contact_details",
    [
        (
            {"name": "John Doe"},
            ContactDetails(name="John Doe"),
        ),
        (
            {
                "name": "Michael Smith",
                "email": "michael.smith@example.com",
                "phone_number": "123-456-7890",
                "linkedin": "https://www.linkedin.com/in/michaelsmith",
                "github": "https://github.com/michaelsmith",
                "other_links": [
                    "https://www.michaelsmith.com",
                    "https://www.michaelsmithblog.com",
                ],
            },
            ContactDetails(
                name="Michael Smith",
                email="michael.smith@example.com",
                phone_number="123-456-7890",
                linkedin="https://www.linkedin.com/in/michaelsmith",
                github="https://github.com/michaelsmith",
                other_links=[
                    "https://www.michaelsmith.com",
                    "https://www.michaelsmithblog.com",
                ],
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_contact_details(example_data, expected_contact_details):
    assert build_contact_details(example_data) == expected_contact_details


@pytest.mark.parametrize(
    "example_data, expected_person",
    [
        (
            {
                "cai_hash": "abc123",
                "id": "person1",
                "name": "John Doe",
                "relation_type": "friend",
                "is_reference": False,
            },
            Person(
                cai_hash="abc123",
                id="person1",
                name="John Doe",
                relation_type="friend",
                is_reference=False,
            ),
        ),
        (
            {
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
                    "other_links": [
                        "https://www.michaelsmith.com",
                        "https://www.michaelsmithblog.com",
                    ],
                },
            },
            Person(
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
                    other_links=[
                        "https://www.michaelsmith.com",
                        "https://www.michaelsmithblog.com",
                    ],
                ),
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_person(example_data, expected_person, basic_user):
    assert build_person(example_data, basic_user) == expected_person


@pytest.mark.parametrize(
    "example_data, expected_qualification",
    [
        (
            {
                "id": "qual1",
                "name": "Bachelor's Degree",
                "studied_at": "University of Example",
                "awarded_date": "2020-06-01",
                "cai_hash": "qualhash123",
            },
            Qualification(
                id="qual1",
                name="Bachelor's Degree",
                studied_at="University of Example",
                awarded_date=datetime.strptime("2020-06-01", "%Y-%m-%d").date(),
                cai_hash="qualhash123",
            ),
        ),
        (
            {
                "id": "qual2",
                "name": "Master's Degree",
                "studied_at": "Example University",
                "awarded_date": "2022-05-15",
                "cai_hash": "qualhash456",
                "grade": "A",
                "expiration_date": "2030-05-15",
                "comment": "Graduated with honors.",
                "related_skills": ["Research", "Data Analysis"],
                "tags": ["Education", "Higher Education"],
            },
            Qualification(
                id="qual2",
                name="Master's Degree",
                studied_at="Example University",
                awarded_date=datetime.strptime("2022-05-15", "%Y-%m-%d").date(),
                cai_hash="qualhash456",
                grade="A",
                expiration_date=datetime.strptime("2030-05-15", "%Y-%m-%d").date(),
                comment="Graduated with honors.",
                related_skills={"Research", "Data Analysis"},
                tags={"Education", "Higher Education"},
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_qualification(example_data, expected_qualification):
    assert build_qualification(example_data) == expected_qualification


@pytest.mark.parametrize(
    "example_data, expected_hobby",
    [
        (
            {
                "name": "Photography",
                "id": "hobby1",
                "cai_hash": "hobbyhash123",
                "description": "I point a camera at things yo",
            },
            Hobby(
                name="Photography",
                id="hobby1",
                cai_hash="hobbyhash123",
                description="I point a camera at things yo",
            ),
        ),
        (
            {
                "name": "Traveling",
                "description": "Exploring new places and cultures around the world.",
                "cai_hash": "hobbyhash123",
                "comment": "I have visited over 30 countries and counting!",
                "tags": ["Adventure", "Culture", "Food"],
                "awards_or_accolades": [
                    "Best Travel Blogger 2023",
                    "Top 10 Travel Influencers 2022",
                ],
                "related_skills": [
                    "Cultural Awareness",
                    "Language Skills",
                    "Photography",
                ],
                "id": "hobby2",
            },
            Hobby(
                name="Traveling",
                description="Exploring new places and cultures around the world.",
                cai_hash="hobbyhash123",
                comment="I have visited over 30 countries and counting!",
                tags={"Adventure", "Culture", "Food"},
                awards_or_accolades={
                    "Best Travel Blogger 2023",
                    "Top 10 Travel Influencers 2022",
                },
                related_skills={"Cultural Awareness", "Language Skills", "Photography"},
                id="hobby2",
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_hobby(example_data, expected_hobby):
    assert build_hobby(example_data) == expected_hobby


@pytest.mark.parametrize(
    "example_data, expected_project",
    [
        (
            {
                "id": "project1",
                "name": "Personal Website",
                "description": "A simple personal website built with HTML, CSS, and JavaScript.",
                "cai_hash": "projecthash123",
            },
            Project(
                id="project1",
                name="Personal Website",
                description="A simple personal website built with HTML, CSS, and JavaScript.",
                cai_hash="projecthash123",
            ),
        ),
        (
            {
                "id": "project2",
                "name": "E-commerce Platform",
                "description": "A full-featured e-commerce platform built with Django and React.",
                "cai_hash": "projecthash456",
                "start_date": "2021-01-01",
                "end_date": "2021-12-31",
                "related_skills": ["Web Development", "Django", "React", "JavaScript"],
                "comment": "This project was a major milestone in my career and received positive feedback from users.",
            },
            Project(
                id="project2",
                name="E-commerce Platform",
                description="A full-featured e-commerce platform built with Django and React.",
                cai_hash="projecthash456",
                start_date=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
                end_date=datetime.strptime("2021-12-31", "%Y-%m-%d").date(),
                related_skills={"Web Development", "Django", "React", "JavaScript"},
                comment="This project was a major milestone in my career and received positive feedback from users.",
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_project(example_data, expected_project):
    assert build_project(example_data) == expected_project


@pytest.mark.parametrize(
    "example_data, expected_skill",
    [
        (
            {
                "id": "skill1",
                "name": "Python",
                "cai_hash": "skillhash123",
            },
            Skill(
                id="skill1",
                name="Python",
                cai_hash="skillhash123",
            ),
        ),
        (
            {
                "id": "skill2",
                "name": "Software Engineering",
                "cai_hash": "skillhash456",
                "proficiency_level": "Advanced",
                "enjoyment_level": 9,
                "tags": {"Backend", "Architecture", "Testing"},
                "related_placements": {"placement1", "placement2"},
                "related_projects": {"project1", "project2"},
                "related_qualifications": {"qual1", "qual2"},
            },
            Skill(
                id="skill2",
                name="Software Engineering",
                cai_hash="skillhash456",
                proficiency_level="Advanced",
                enjoyment_level=9,
                tags={"Backend", "Architecture", "Testing"},
                related_placements={"placement1", "placement2"},
                related_projects={"project1", "project2"},
                related_qualifications={"qual1", "qual2"},
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_skill(example_data, expected_skill):
    assert build_skill(example_data) == expected_skill


@pytest.mark.parametrize(
    "example_data, expected_placement",
    [
        (
            {
                "id": "placement1",
                "name": "Example Corp",
                "job_title": "Junior Developer",
                "start_date": datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
                "end_date": datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
                "cai_hash": "placementhash123",
            },
            Placement(
                id="placement1",
                name="Example Corp",
                job_title="Junior Developer",
                start_date=datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
                end_date=datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
                cai_hash="placementhash123",
            ),
        ),
        (
            {
                "id": "placement2",
                "name": "Tech Solutions Ltd",
                "job_title": "Senior Engineer",
                "start_date": datetime.strptime("2023-02-01", "%Y-%m-%d").date(),
                "end_date": datetime.strptime("2025-02-01", "%Y-%m-%d").date(),
                "cai_hash": "placementhash456",
                "reason_for_leaving": "Pursued a new leadership opportunity",
                "related_projects": {"project1", "project2"},
                "reference_contacts": {"person1", "person2"},
                "related_skills": {"skill1", "skill2"},
            },
            Placement(
                id="placement2",
                name="Tech Solutions Ltd",
                job_title="Senior Engineer",
                start_date=datetime.strptime("2023-02-01", "%Y-%m-%d").date(),
                end_date=datetime.strptime("2025-02-01", "%Y-%m-%d").date(),
                cai_hash="placementhash456",
                reason_for_leaving="Pursued a new leadership opportunity",
                project_references={"project1", "project2"},
                reference_contacts={"person1", "person2"},
                related_skills={"skill1", "skill2"},
            ),
        ),
    ],
    ids=["minimum", "maximum"],
)
def test_build_placement(example_data, expected_placement):
    assert build_placement(example_data) == expected_placement

#TODO Do I need to test CAI hashing? it's just a hash of other fields?

def test_parse_data(mocker):
    root_dir = "tests/test_data/"
    test_data = [
        (dataclass_type.SKILL, "parse_data_skills.yaml", "hash"),
        (dataclass_type.PLACEMENT, "parse_data_placements.yaml", "hash"),
        (dataclass_type.QUALIFICATION, "parse_data_qualifications.yaml", "hash"),
        (dataclass_type.HOBBY, "parse_data_hobbies.yaml", "hash"),
        (dataclass_type.PROJECT, "parse_data_projects.yaml", "hash"),
        (dataclass_type.PERSON, "parse_data_persons.yaml", "hash")
    ]



    mock_validate_data = mocker.patch('src.models.data_ingestion.validate_data')
    mock_build_skill = mocker.patch('src.models.data_ingestion.build_skill')
    mock_build_placement = mocker.patch('src.models.data_ingestion.build_placement')
    mock_build_qualification = mocker.patch('src.models.data_ingestion.build_qualification')
    mock_build_hobby = mocker.patch('src.models.data_ingestion.build_hobby')
    mock_build_project = mocker.patch('src.models.data_ingestion.build_project')
    mock_build_person = mocker.patch('src.models.data_ingestion.build_person')
    mock_user_add_data = mocker.patch('src.models.user.User.add_data')



#TODO HERE 
    