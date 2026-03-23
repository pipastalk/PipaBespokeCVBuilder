from datetime import date

from src.logic.data_tools import get_multi_skill_related_context, get_skill_related_context, search_user_skills
from src.models.AdvertSourceType import AdvertSourceType
from src.models.User import User
from src.models.dataclass_type import dataclass_type
from src.models.schema import Advert, AdvertSource, ContactDetails, Hobby, Location, Placement, Project, Qualification, Skill


def _build_advert(required_skills: set[str], desired_skills: set[str]) -> Advert:
    return Advert(
        advert_title="Senior BI Analyst",
        advert_description="Role focused on BI and SQL delivery.",
        source=AdvertSource(
            source_path="https://example.com/job",
            sourced_from="example.com",
            source_type=AdvertSourceType.WEBSITE,
        ),
        placement_location=Location(city="Leicester", country="GB"),
        working_pattern="Hybrid",
        contact_details=ContactDetails(name="Hiring Manager"),
        advertStyle="hybrid",
        required_skills=required_skills,
        desired_skills=desired_skills,
    )


def test_search_user_skills_matches_on_skill_name_not_id():
    user = User(name="Pippa")
    user.add_data(Skill(id="sql-core-SKILL", name="SQL", cai_hash="h1"), dataclass_type.SKILL)
    user.add_data(Skill(id="bi-reporting-SKILL", name="Power BI", cai_hash="h2"), dataclass_type.SKILL)

    advert = _build_advert(required_skills={"SQL"}, desired_skills={"Power BI", "Python"})

    result = search_user_skills(user, advert)

    assert result["matched_user_skill_ids"] == ["bi-reporting-SKILL", "sql-core-SKILL"]
    assert len(result["matching_required_skills"]) == 1
    assert len(result["matching_desired_skills"]) == 1
    assert result["missing_required_skills"] == []
    assert result["missing_desired_skills"] == ["Python"]


def test_get_skill_related_context_returns_linked_entities():
    user = User(name="Pippa")

    skill = Skill(
        id="sql-core-SKILL",
        name="SQL",
        cai_hash="h-sql",
        related_projects={"bi-dashboard-1-PROJECT"},
        related_placements={"acme-data-analyst-PLACEMENT"},
        related_qualifications={"bsc-compsci-QUALIFICATION"},
        related_hobbies={"chess-HOBBY"},
    )
    user.add_data(skill, dataclass_type.SKILL)

    user.add_data(
        Project(
            id="bi-dashboard-1-PROJECT",
            name="BI Dashboard",
            description="Created KPI dashboard in SQL and BI.",
            cai_hash="h-proj",
        ),
        dataclass_type.PROJECT,
    )
    user.add_data(
        Placement(
            id="acme-data-analyst-PLACEMENT",
            name="ACME",
            job_title="Data Analyst",
            start_date=date(2022, 1, 1),
            end_date=date(2023, 1, 1),
            cai_hash="h-place",
        ),
        dataclass_type.PLACEMENT,
    )
    user.add_data(
        Qualification(
            id="bsc-compsci-QUALIFICATION",
            name="BSc Computer Science",
            studied_at="Example University",
            awarded_date=date(2020, 6, 1),
            cai_hash="h-qual",
        ),
        dataclass_type.QUALIFICATION,
    )
    user.add_data(
        Hobby(
            id="chess-HOBBY",
            name="Chess",
            description="Competitive chess player.",
            cai_hash="h-hobby",
        ),
        dataclass_type.HOBBY,
    )

    result = get_skill_related_context(user, "sql-core-SKILL")

    assert result["skill"]["id"] == "sql-core-SKILL"
    assert len(result["related_context"]["related_projects"]) == 1
    assert len(result["related_context"]["related_placements"]) == 1
    assert len(result["related_context"]["related_qualifications"]) == 1
    assert len(result["related_context"]["related_hobbies"]) == 1


def test_get_multi_skill_related_context_returns_all_skill_blocks():
    user = User(name="Pippa")
    user.add_data(Skill(id="sql-core-SKILL", name="SQL", cai_hash="h1"), dataclass_type.SKILL)
    user.add_data(Skill(id="python-SKILL", name="Python", cai_hash="h2"), dataclass_type.SKILL)

    result = get_multi_skill_related_context(user, ["sql-core-SKILL", "python-SKILL"])

    assert len(result["skills"]) == 2
    assert result["skills"][0]["skill"]["id"] == "sql-core-SKILL"
    assert result["skills"][1]["skill"]["id"] == "python-SKILL"
