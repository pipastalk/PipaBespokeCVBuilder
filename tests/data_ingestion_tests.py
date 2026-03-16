import pytest
from datetime import date, datetime
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


def test_read_yaml_file_returns_all_documents(tmp_path):
    test_yaml = tmp_path / "multi_doc.yaml"
    test_yaml.write_text("""name: one\n---\nname: two\n""")

    data = read_yaml_file(str(test_yaml))

    assert data == [{"name": "one"}, {"name": "two"}]


def test_read_yaml_file_missing_path_raises_value_error():
    with pytest.raises(ValueError):
        read_yaml_file("/path/that/does/not/exist.yaml")


def test_get_required_fields_returns_expected_values():
    fields = get_required_fields(dataclass_type.SKILL)

    assert fields == ["name", "cai_hash"]


def test_get_required_fields_invalid_type_raises_value_error():
    with pytest.raises(ValueError):
        get_required_fields(None)


def test_convert_date_none_returns_none():
    assert convert_date(None) is None


def test_convert_date_datetime_returns_date():
    dt = datetime(2024, 1, 15, 8, 30)

    assert convert_date(dt) == date(2024, 1, 15)


def test_convert_date_string_valid_format():
    assert convert_date("16-03-2026") == date(2026, 3, 16)


def test_convert_date_string_invalid_format_raises_value_error():
    with pytest.raises(ValueError):
        convert_date("2026-03-16")


def test_build_cai_hash_is_stable_for_key_order():
    left = {"name": "python", "level": 3}
    right = {"level": 3, "name": "python"}

    assert build_cai_hash(left) == build_cai_hash(right)


def test_generate_unique_id_retries_until_success(mocker, basic_user):
    data = {"name": "Python", "cai_hash": "abcdef"}
    mock_generate = mocker.patch.object(basic_user, "generate_id")
    mock_generate.side_effect = [
        DuplicateItemIDExists("x", dataclass_type.SKILL),
        "python-skill-id",
    ]

    generated_id = generate_unique_id(data, dataclass_type.SKILL, basic_user)

    assert generated_id == "python-skill-id"
    assert mock_generate.call_count == 2


def test_generate_unique_id_raises_critical_after_max_attempts(mocker, basic_user):
    data = {"name": "Python", "cai_hash": "abc"}
    mock_generate = mocker.patch.object(basic_user, "generate_id")
    mock_generate.side_effect = DuplicateItemExists("x", dataclass_type.SKILL)

    with pytest.raises(CriticalDuplicateItemExists):
        generate_unique_id(data, dataclass_type.SKILL, basic_user)

    assert mock_generate.call_count == len(data["cai_hash"])


def test_validate_data_empty_payload_raises_value_error(basic_user):
    with pytest.raises(ValueError):
        validate_data({}, dataclass_type.SKILL, basic_user)


def test_validate_data_duplicate_hash_raises_duplicate_item_exists(mocker, basic_user):
    payload = {"name": "Python", "cai_hash": "hash123"}
    existing = Skill(name="Python", id="skill-1", cai_hash="hash123")
    mocker.patch.object(basic_user, "hash_search", return_value=(existing, dataclass_type.SKILL))

    with pytest.raises(DuplicateItemExists):
        validate_data(payload, dataclass_type.SKILL, basic_user)


def test_validate_data_generates_hash_id_and_converts_date(mocker, basic_user):
    payload = {
        "id": "input-id",
        "name": "Backend Engineer",
        "job_title": "Engineer",
        "start_date": "01-02-2024",
        "related_skills": [{"name": "Python", "cai_hash": "skillhash"}],
    }
    mocker.patch.object(basic_user, "hash_search", return_value=None)
    mocker.patch("src.models.data_ingestion.generate_unique_id", return_value="placement-1")
    mocker.patch("src.models.data_ingestion.create_missing_related_items", return_value=["skill-1"])

    validated = validate_data(payload, dataclass_type.PLACEMENT, basic_user)

    assert validated["cai_hash"]
    assert validated["id"] == "placement-1"
    assert validated["start_date"] == date(2024, 2, 1)
    assert validated["related_skills"] == ["skill-1"]


def test_validate_data_missing_required_field_raises_value_error(mocker, basic_user):
    payload = {"id": "skill-id", "cai_hash": "hash123"}
    mocker.patch.object(basic_user, "hash_search", return_value=None)

    with pytest.raises(ValueError):
        validate_data(payload, dataclass_type.SKILL, basic_user)


def test_create_missing_related_items_builds_and_adds_new_item(mocker, basic_user):
    raw_item = {"name": "Python", "cai_hash": "skillhash"}
    built_item = Skill(name="Python", id="python-skill-id", cai_hash="skillhash")
    mocker.patch("src.models.data_ingestion.build_cai_hash", return_value="skillhash")
    mocker.patch.object(basic_user, "hash_search", return_value=None)
    mocker.patch("src.models.data_ingestion.validate_data", return_value={"name": "Python", "id": "python-skill-id", "cai_hash": "skillhash"})
    mocker.patch("src.models.data_ingestion.build_skill", return_value=built_item)

    ids = create_missing_related_items([raw_item], dataclass_type.SKILL, basic_user)

    assert ids == ["python-skill-id"]
    assert basic_user.get_item("python-skill-id", dataclass_type.SKILL) == built_item


def test_create_missing_related_items_reuses_existing_item(mocker, basic_user):
    existing_item = Skill(name="Python", id="python-skill-id", cai_hash="skillhash")
    basic_user.add_data(existing_item, dataclass_type.SKILL)
    mocker.patch("src.models.data_ingestion.build_cai_hash", return_value="skillhash")
    mocker.patch.object(basic_user, "hash_search", return_value=(existing_item, dataclass_type.SKILL))
    validate_spy = mocker.patch("src.models.data_ingestion.validate_data")

    ids = create_missing_related_items([{"name": "Python", "cai_hash": "skillhash"}], dataclass_type.SKILL, basic_user)

    assert ids == ["python-skill-id"]
    validate_spy.assert_not_called()


def test_create_missing_related_items_wrong_dataclass_type_raises_value_error(mocker, basic_user):
    orphan_item = Skill(name="Python", id="python-skill-id", cai_hash="skillhash")
    mocker.patch("src.models.data_ingestion.build_cai_hash", return_value="skillhash")
    mocker.patch.object(basic_user, "hash_search", return_value=(orphan_item, dataclass_type.SKILL))

    with pytest.raises(ValueError):
        create_missing_related_items([{"name": "Python", "cai_hash": "skillhash"}], dataclass_type.PROJECT, basic_user)


@pytest.mark.parametrize(
    "d_type,builder_name,data,created",
    [
        (
            dataclass_type.SKILL,
            "build_skill",
            {"id": "skill-id", "name": "Python", "cai_hash": "hash-skill"},
            Skill(id="skill-id", name="Python", cai_hash="hash-skill"),
        ),
        (
            dataclass_type.PROJECT,
            "build_project",
            {"id": "project-id", "name": "Proj", "description": "desc", "cai_hash": "hash-proj"},
            Project(id="project-id", name="Proj", description="desc", cai_hash="hash-proj"),
        ),
    ],
)
def test_parse_data_calls_builder_and_adds_items(mocker, basic_user, d_type, builder_name, data, created):
    mocker.patch("src.models.data_ingestion.read_yaml_file", return_value=[data])
    mocker.patch("src.models.data_ingestion.validate_data", return_value=data)
    mock_builder = mocker.patch(f"src.models.data_ingestion.{builder_name}", return_value=created)

    parse_data("fake_path.yaml", d_type, basic_user)

    mock_builder.assert_called_once_with(data)
    assert basic_user.get_item(created.id, d_type) == created


def test_parse_data_calls_person_builder_with_user(mocker, basic_user):
    data = {
        "id": "person-1",
        "name": "Jane",
        "cai_hash": "personhash",
        "relation_type": "friend",
        "is_reference": False,
        "contact_details": {"name": "Jane"},
    }
    created = Person(
        id="person-1",
        name="Jane",
        cai_hash="personhash",
        relation_type="friend",
        is_reference=False,
        contact_details=ContactDetails(name="Jane"),
    )
    mocker.patch("src.models.data_ingestion.read_yaml_file", return_value=[data])
    mocker.patch("src.models.data_ingestion.validate_data", return_value=data)
    mock_builder = mocker.patch("src.models.data_ingestion.build_person", return_value=created)

    parse_data("fake_people.yaml", dataclass_type.PERSON, basic_user)

    mock_builder.assert_called_once_with(data, basic_user)
    assert basic_user.get_item("person-1", dataclass_type.PERSON) == created


def test_parse_data_unsupported_dataclass_type_raises_not_implemented(basic_user):
    with pytest.raises(NotImplementedError):
        parse_data("fake_path.yaml", dataclass_type.CONTACT_DETAILS, basic_user)


def test_parse_data_empty_entry_raises_value_error(mocker, basic_user):
    mocker.patch("src.models.data_ingestion.read_yaml_file", return_value=[None])

    with pytest.raises(ValueError):
        parse_data("fake_path.yaml", dataclass_type.SKILL, basic_user)


def test_merge_matched_data_currently_returns_none(basic_user):
    assert merge_matched_data({}, "hash", dataclass_type.SKILL, basic_user) is None


