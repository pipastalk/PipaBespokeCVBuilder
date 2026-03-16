import pytest
from datetime import date
from src.models.dataclass_type import dataclass_type
from src.models.data_ingestion import *
from src.models.schema import *




#region pytest fixtures
@pytest.fixture
def basic_user():
    return User("Test User")


#region contact details fixtures
@pytest.fixture
def example_minimum_contact_detail():
    return ContactDetails(name="John Doe")


@pytest.fixture
def example_minimum_contact_detail_data():
    return {"name": "John Doe"}


@pytest.fixture
def example_maximum_contact_detail():
    return ContactDetails(
        name="Michael Smith",
        email="michael.smith@example.com",
        phone_number="123-456-7890",
        linkedin="https://www.linkedin.com/in/michaelsmith",
        github="https://github.com/michaelsmith",
        other_links=[
            "https://www.michaelsmith.com",
            "https://www.michaelsmithblog.com",
        ]
    )


@pytest.fixture
def example_maximum_contact_detail_data():
    return {
        "name": "Michael Smith",
        "email": "michael.smith@example.com",
        "phone_number": "123-456-7890",
        "linkedin": "https://www.linkedin.com/in/michaelsmith",
        "github": "https://github.com/michaelsmith",
        "other_links": [
            "https://www.michaelsmith.com",
            "https://www.michaelsmithblog.com",
        ]
    }


#endregion

#region person fixtures
@pytest.fixture
def example_minimum_person_data():
    return {
        "cai_hash": "abc123",
        "id": "person1",
        "name": "John Doe",
        "relation_type": "friend",
        "is_reference": False,
        "contact_details": {
            "name": "John Doe",
        }
    }


@pytest.fixture
def example_minimum_person():
    return Person(
        cai_hash="abc123",
        id="person1",
        name="John Doe",
        relation_type="friend",
        is_reference=False,
        contact_details=ContactDetails(name="John Doe")
    )


@pytest.fixture
def example_maximum_person():
    return Person(
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
            ]
        )
    )


@pytest.fixture
def example_maximum_person_data():
    return {
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
        }
    }


#endregion

#region qualification fixtures
@pytest.fixture
def example_minimum_qualification_data():
    return {
        "id": "qual1",
        "name": "Bachelor's Degree",
        "studied_at": "University of Example",
        "awarded_date": date(2020, 6, 1),
        "cai_hash": "qualhash123",
        "grade": None
    }


@pytest.fixture
def example_minimum_qualification():
    return Qualification(
        id="qual1",
        name="Bachelor's Degree",
        studied_at="University of Example",
        awarded_date=date(2020, 6, 1),
        cai_hash="qualhash123"
    )


@pytest.fixture
def example_maximum_qualification_data():
    return {
        "id": "qual2",
        "name": "Master's Degree",
        "studied_at": "Example University",
        "awarded_date": date(2022, 5, 15),
        "cai_hash": "qualhash456",
        "grade": "A",
        "expiration_date": date(2030, 5, 15),
        "comment": "Graduated with honors.",
        "related_skills": {"Research", "Data Analysis"},
        "tags": {"Education", "Higher Education"}
    }


@pytest.fixture
def example_maximum_qualification():
    return Qualification(
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


#endregion

#region hobby fixtures
@pytest.fixture
def example_minimum_hobby():
    return Hobby(
        name="Photography",
        id="hobby1",
        cai_hash="hobbyhash123",
        description="I point a camera at things yo"
    )


@pytest.fixture
def example_minimum_hobby_data():
    return {
        "name": "Photography",
        "id": "hobby1",
        "cai_hash": "hobbyhash123",
        "description": "I point a camera at things yo"
    }


@pytest.fixture
def example_maximum_hobby():
    return Hobby(
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
        id="hobby2"
    )


@pytest.fixture
def example_maximum_hobby_data():
    return {
        "name": "Traveling",
        "description": "Exploring new places and cultures around the world.",
        "cai_hash": "hobbyhash123",
        "comment": "I have visited over 30 countries and counting!",
        "tags": {"Adventure", "Culture", "Food"},
        "awards_or_accolades": {
            "Best Travel Blogger 2023",
            "Top 10 Travel Influencers 2022",
        },
        "related_skills": {"Cultural Awareness", "Language Skills", "Photography"},
        "id": "hobby2"
    }


#endregion

#region project fixtures
@pytest.fixture
def example_minimum_project():
    return Project(
        id="project1",
        name="Personal Website",
        description="A simple personal website built with HTML, CSS, and JavaScript.",
        cai_hash="projecthash123",
    )


@pytest.fixture
def example_minimum_project_data():
    return {
        "id": "project1",
        "name": "Personal Website",
        "description": "A simple personal website built with HTML, CSS, and JavaScript.",
        "cai_hash": "projecthash123",
    }


@pytest.fixture
def example_maximum_project():
    return Project(
        id="project2",
        name="E-commerce Platform",
        description="A full-featured e-commerce platform built with Django and React.",
        cai_hash="projecthash456",
        start_date=date(2021, 1, 1),
        end_date=date(2021, 12, 31),
        related_skills={"Web Development", "Django", "React", "JavaScript"},
        comment="This project was a major milestone in my career and received positive feedback from users.",
    )


@pytest.fixture
def example_maximum_project_data():
    return {
        "id": "project2",
        "name": "E-commerce Platform",
        "description": "A full-featured e-commerce platform built with Django and React.",
        "cai_hash": "projecthash456",
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 12, 31),
        "related_skills": {"Web Development", "Django", "React", "JavaScript"},
        "comment": "This project was a major milestone in my career and received positive feedback from users.",
    }


#endregion

#region skill fixtures
@pytest.fixture
def example_minimum_skill():
    return Skill(
        id="skill1",
        name="Python",
        cai_hash="skillhash123",
    )


@pytest.fixture
def example_minimum_skill_data():
    return {
        "id": "skill1",
        "name": "Python",
        "cai_hash": "skillhash123",
    }


@pytest.fixture
def example_maximum_skill():
    return Skill(
        id="skill2",
        name="Software Engineering",
        cai_hash="skillhash456",
        proficiency_level="Advanced",
        enjoyment_level=9,
        tags={"Backend", "Architecture", "Testing"},
        related_placements={"placement1", "placement2"},
        related_projects={"project1", "project2"},
        related_qualifications={"qual1", "qual2"},
    )


@pytest.fixture
def example_maximum_skill_data():
    return {
        "id": "skill2",
        "name": "Software Engineering",
        "cai_hash": "skillhash456",
        "proficiency_level": "Advanced",
        "enjoyment_level": 9,
        "tags": {"Backend", "Architecture", "Testing"},
        "related_placements": {"placement1", "placement2"},
        "related_projects": {"project1", "project2"},
        "related_qualifications": {"qual1", "qual2"},
    }


#endregion

#region placement fixtures
@pytest.fixture
def example_minimum_placement():
    return Placement(
        id="placement1",
        name="Example Corp",
        job_title="Junior Developer",
        start_date=date(2022, 1, 1),
        end_date=date(2023, 1, 1),
        cai_hash="placementhash123",
    )


@pytest.fixture
def example_minimum_placement_data():
    return {
        "id": "placement1",
        "name": "Example Corp",
        "job_title": "Junior Developer",
        "start_date": date(2022, 1, 1),
        "end_date": date(2023, 1, 1),
        "cai_hash": "placementhash123",
    }


@pytest.fixture
def example_maximum_placement():
    return Placement(
        id="placement2",
        name="Tech Solutions Ltd",
        job_title="Senior Engineer",
        start_date=date(2023, 2, 1),
        end_date=date(2025, 2, 1),
        cai_hash="placementhash456",
        reason_for_leaving="Pursued a new leadership opportunity",
        project_references={"project1", "project2"},
        reference_contacts={"person1", "person2"},
        related_skills={"skill1", "skill2"},
    )


@pytest.fixture
def example_maximum_placement_data():
    return {
        "id": "placement2",
        "name": "Tech Solutions Ltd",
        "job_title": "Senior Engineer",
        "start_date": date(2023, 2, 1),
        "end_date": date(2025, 2, 1),
        "cai_hash": "placementhash456",
        "reason_for_leaving": "Pursued a new leadership opportunity",
        "related_projects": {"project1", "project2"},
        "reference_contacts": {"person1", "person2"},
        "related_skills": {"skill1", "skill2"},
    }


#endregion
#endregion 

def test_build_contact_details_minimum(example_minimum_contact_detail_data, example_minimum_contact_detail):
    assert build_contact_details(example_minimum_contact_detail_data) == example_minimum_contact_detail

def test_build_contact_details_maximum(example_maximum_contact_detail_data,example_maximum_contact_detail):
    assert build_contact_details(example_maximum_contact_detail_data) == example_maximum_contact_detail 

def test_build_person_minimum(example_minimum_person_data, example_minimum_person, basic_user):
    assert build_person(example_minimum_person_data, basic_user) == example_minimum_person


def test_build_person_maximum(example_maximum_person_data, example_maximum_person, basic_user):
    assert build_person(example_maximum_person_data, basic_user) == example_maximum_person


def test_build_qualification_minimum(example_minimum_qualification_data, example_minimum_qualification):
    assert build_qualification(example_minimum_qualification_data) == example_minimum_qualification

def test_build_qualification_maximum(example_maximum_qualification_data, example_maximum_qualification):
    assert build_qualification(example_maximum_qualification_data) == example_maximum_qualification


def test_build_hobby_minimum(example_minimum_hobby_data, example_minimum_hobby):
    assert build_hobby(example_minimum_hobby_data) == example_minimum_hobby


def test_build_hobby_maximum(example_maximum_hobby_data, example_maximum_hobby):
    assert build_hobby(example_maximum_hobby_data) == example_maximum_hobby


def test_build_project_minimum(example_minimum_project_data, example_minimum_project):
    assert build_project(example_minimum_project_data) == example_minimum_project


def test_build_project_maximum(example_maximum_project_data, example_maximum_project):
    assert build_project(example_maximum_project_data) == example_maximum_project


def test_build_skill_minimum(example_minimum_skill_data, example_minimum_skill):
    assert build_skill(example_minimum_skill_data) == example_minimum_skill


def test_build_skill_maximum(example_maximum_skill_data, example_maximum_skill):
    assert build_skill(example_maximum_skill_data) == example_maximum_skill


def test_build_placement_minimum(example_minimum_placement_data, example_minimum_placement):
    assert build_placement(example_minimum_placement_data) == example_minimum_placement


def test_build_placement_maximum(example_maximum_placement_data, example_maximum_placement):
    assert build_placement(example_maximum_placement_data) == example_maximum_placement


# TODO Do I need to test CAI hashing? it's just a hash of other fields?


def test_parse_data_with_type(mocker):
    test_data = [
        (example_maximum_contact_detail, dataclass_type.CONTACT_DETAILS, example_maximum_contact_detail_data),
        (example_maximum_hobby, dataclass_type.HOBBY, example_maximum_hobby_data),
        (example_maximum_person, dataclass_type.PERSON, example_maximum_person_data),
        (example_maximum_project, dataclass_type.PROJECT, example_maximum_project_data),
        (example_maximum_qualification, dataclass_type.QUALIFICATION, example_maximum_qualification_data),
        (example_maximum_placement, dataclass_type.PLACEMENT, example_maximum_placement_data),
    ]
    for obj, d_type, data in test_data:
        test_parse_data(mocker, d_type, obj, data, basic_user)
    
def test_parse_data(mocker, d_type, obj_example, data_example, basic_user):
    test_data = {
        dataclass_type.SKILL: mocker.patch("src.models.data_ingestion.build_skill"),
        dataclass_type.PLACEMENT: mocker.patch("src.models.data_ingestion.build_placement"),
        dataclass_type.QUALIFICATION: mocker.patch("src.models.data_ingestion.build_qualification"),
        dataclass_type.HOBBY: mocker.patch("src.models.data_ingestion.build_hobby"),
        dataclass_type.PROJECT: mocker.patch("src.models.data_ingestion.build_project"),
        dataclass_type.PERSON: mocker.patch("src.models.data_ingestion.build_person"),
    }
    mock_read_data = mocker.patch("src.models.data_ingestion.read_data_file")
    mock_read_data.return_value = data_example
    mock_validate_data = mocker.patch("src.models.data_ingestion.validate_data")
    mock_validate_data.return_value = data_example
    mock_build = test_data[d_type]
    mock_build.return_value = obj_example
    parse_data("fake_path.yaml", d_type, basic_user)
    mock_read_data.assert_called_once_with("fake_path.yaml")
    mock_validate_data.assert_called_once_with(data_example, d_type, basic_user)
    mock_build.assert_called_once_with(data_example, basic_user)
    #file_data = read_yaml_file(file_path)
    #validated_data = validate_data(entry, d_type, user)
    #finished_entry = build(validated_data, user)
    user_dict = basic_user.get_dict(d_type)
    assert user_dict[obj_example.id] == obj_example


