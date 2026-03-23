import re
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from difflib import SequenceMatcher
from typing import Any, cast

from src.exceptions.user_exceptions import ItemNotFoundInUserDict
from src.models.User import User
from src.models.dataclass_type import dataclass_type
from src.models.schema import Advert, Skill


def _normalize_skill_name(skill_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", skill_name.lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def _serialize(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(_serialize(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if is_dataclass(value):
        return _serialize(asdict(cast(Any, value)))
    return value


def _to_skill_name(value: Any) -> str:
    if isinstance(value, Skill):
        return value.name
    if isinstance(value, str):
        return value
    return str(value)


def _skill_text_matches(advert_skill_name: str, user_skill_name: str, threshold: float = 0.84) -> bool:
    left = _normalize_skill_name(advert_skill_name)
    right = _normalize_skill_name(user_skill_name)

    if not left or not right:
        return False
    if left == right:
        return True
    if left in right or right in left:
        return True

    ratio = SequenceMatcher(None, left, right).ratio()
    return ratio >= threshold


def _match_advert_skill_to_user_skills(user: User, advert_skill_name: str) -> list[Skill]:
    matches: list[Skill] = []
    for skill in user.skills.values():
        if _skill_text_matches(advert_skill_name, skill.name):
            matches.append(skill)
    return matches


def _skill_match_payload(advert_skill_name: str, skill: Skill) -> dict[str, str]:
    return {
        "advert_skill": advert_skill_name,
        "user_skill_id": skill.id,
        "user_skill_name": skill.name,
    }


def search_user_skills(user: User, advert: Advert) -> dict[str, Any]:
    required_skill_names = sorted(_to_skill_name(skill) for skill in (advert.required_skills or []))
    desired_skill_names = sorted(_to_skill_name(skill) for skill in (advert.desired_skills or []))

    matching_required_skills: list[dict[str, str]] = []
    matching_desired_skills: list[dict[str, str]] = []
    missing_required_skills: list[str] = []
    missing_desired_skills: list[str] = []
    matched_user_skill_ids: set[str] = set()

    for advert_skill_name in required_skill_names:
        matches = _match_advert_skill_to_user_skills(user, advert_skill_name)
        if not matches:
            missing_required_skills.append(advert_skill_name)
            continue
        for skill in matches:
            matching_required_skills.append(_skill_match_payload(advert_skill_name, skill))
            matched_user_skill_ids.add(skill.id)

    for advert_skill_name in desired_skill_names:
        matches = _match_advert_skill_to_user_skills(user, advert_skill_name)
        if not matches:
            missing_desired_skills.append(advert_skill_name)
            continue
        for skill in matches:
            matching_desired_skills.append(_skill_match_payload(advert_skill_name, skill))
            matched_user_skill_ids.add(skill.id)

    return {
        "matching_required_skills": matching_required_skills,
        "matching_desired_skills": matching_desired_skills,
        "missing_required_skills": missing_required_skills,
        "missing_desired_skills": missing_desired_skills,
        "matched_user_skill_ids": sorted(matched_user_skill_ids),
    }


def get_related_item(user: User, id: str, field: str):
    related_sets_map = {
        "related_placements": dataclass_type.PLACEMENT,
        "related_projects": dataclass_type.PROJECT,
        "related_qualifications": dataclass_type.QUALIFICATION,
        "related_hobbies": dataclass_type.HOBBY,
    }
    d_type = related_sets_map.get(field)
    if not d_type:
        raise ValueError(f"Invalid field: {field}")
    item = user.get_item(id, d_type)
    if item is None:
        raise ItemNotFoundInUserDict(id, d_type)
    return item


def get_skill_related_context(user: User, skill_id: str) -> dict[str, Any]:
    skill = user.get_item(skill_id, dataclass_type.SKILL)
    if not isinstance(skill, Skill):
        raise ItemNotFoundInUserDict(skill_id, dataclass_type.SKILL)

    fields = [
        "related_projects",
        "related_placements",
        "related_qualifications",
        "related_hobbies",
    ]

    related_context: dict[str, list[Any]] = {}
    for field in fields:
        related_ids = sorted(getattr(skill, field, set()))
        related_context[field] = [_serialize(get_related_item(user, item_id, field)) for item_id in related_ids]

    return {
        "skill": _serialize(skill),
        "related_context": related_context,
    }


def get_multi_skill_related_context(user: User, skill_ids: list[str]) -> dict[str, Any]:
    return {
        "skills": [get_skill_related_context(user, skill_id) for skill_id in skill_ids],
    }


