import argparse
import os
from urllib.parse import urlparse

from src.logic.gemini import GeminiLLM
from src.logging import prep_loggers
from src.models.AdvertSourceType import AdvertSourceType
from src.models.User import User
from src.models.data_ingestion import build_contact_details, build_location, parse_data
from src.models.dataclass_type import dataclass_type
from src.models.schema import Advert, AdvertSource


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def _prompt_if_missing(value: str | None, prompt_text: str) -> str:
    if value and value.strip():
        return value.strip()
    return input(prompt_text).strip()


def _build_user_from_data_files(user_data_dir: str) -> User:
    user = User(name="Pippa")

    parse_plan = [
        ("skills.yaml", dataclass_type.SKILL),
        ("projects.yaml", dataclass_type.PROJECT),
        ("placements.yaml", dataclass_type.PLACEMENT),
        ("references.yaml", dataclass_type.PERSON),
        ("people.yaml", dataclass_type.PERSON),
        ("qualifications.yaml", dataclass_type.QUALIFICATION),
        ("hobbies.yaml", dataclass_type.HOBBY),
    ]

    for filename, d_type in parse_plan:
        file_path = os.path.join(user_data_dir, filename)
        if os.path.exists(file_path):
            parse_data(file_path, d_type, user)

    return user


def _build_advert_from_extraction(extracted_advert) -> Advert:
    return Advert(
        advert_title=extracted_advert.advert_title,
        advert_description=extracted_advert.advert_description,
        source=AdvertSource(
            source_path=extracted_advert.source.source_path,
            sourced_from=extracted_advert.source.sourced_from,
            source_type=AdvertSourceType.WEBSITE,
            comment=extracted_advert.source.comment,
        ),
        placement_location=build_location(extracted_advert.placement_location.model_dump()),
        working_pattern=extracted_advert.working_pattern,
        contact_details=build_contact_details(extracted_advert.contact_details.model_dump()),
        advertStyle=extracted_advert.advertStyle,
        required_skills=set(extracted_advert.required_skills),
        desired_skills=set(extracted_advert.desired_skills),
    )


def main():
    prep_loggers()

    parser = argparse.ArgumentParser(
        description="Generate a tailored CV from a job advert URL and your profile data."
    )
    parser.add_argument("--job-url", help="Job advert URL to process")
    parser.add_argument("--output-dir", help="Directory where CV output files will be saved")
    parser.add_argument(
        "--user-data-dir",
        help="Directory containing user YAML files (e.g. skills.yaml, projects.yaml, placements.yaml)",
    )
    args = parser.parse_args()

    job_url = _prompt_if_missing(args.job_url, "Enter job advert URL: ")
    while not _is_valid_url(job_url):
        print("Invalid URL. Please include scheme and host, e.g. https://example.com/job")
        job_url = input("Enter job advert URL: ").strip()

    output_dir = _prompt_if_missing(args.output_dir, "Enter output directory for CV files: ")
    if not output_dir:
        output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    user_data_dir = _prompt_if_missing(
        args.user_data_dir,
        "Enter user data directory (e.g. data/CV_Resources/Personal): ",
    )
    if not user_data_dir:
        user_data_dir = "data/CV_Resources/Personal"
    while not os.path.isdir(user_data_dir):
        print(f"Directory not found: {user_data_dir}")
        user_data_dir = input("Enter user data directory: ").strip()

    expected_yaml_files = ["skills.yaml", "projects.yaml", "placements.yaml"]
    found_yaml_files = [name for name in expected_yaml_files if os.path.exists(os.path.join(user_data_dir, name))]
    if not found_yaml_files:
        raise ValueError(
            "No expected YAML files were found in user data directory. "
            "Expected at least one of: skills.yaml, projects.yaml, placements.yaml"
        )

    gemini = GeminiLLM()
    sourced_from = urlparse(job_url).netloc
    advert_yaml_path = os.path.join(output_dir, "advert.yaml")

    extracted_advert, _ = gemini.extract_advert_yaml_from_webpage(
        webpage_url=job_url,
        output_yaml_path=advert_yaml_path,
        sourced_from=sourced_from,
    )

    advert = _build_advert_from_extraction(extracted_advert)
    user = _build_user_from_data_files(user_data_dir)

    cv_markdown = gemini.generate_tailored_cv(user=user, advert=advert)
    cv_path = os.path.join(output_dir, "tailored_cv.md")
    with open(cv_path, "w", encoding="utf-8") as cv_file:
        cv_file.write(cv_markdown)

    print(f"Advert YAML saved to: {advert_yaml_path}")
    print(f"Tailored CV saved to: {cv_path}")


if __name__ == "__main__":
    main()
