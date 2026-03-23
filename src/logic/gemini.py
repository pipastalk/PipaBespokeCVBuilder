import json
import logging
import os
import re
from enum import Enum
from typing import cast
from urllib.error import URLError
from urllib.request import Request, urlopen

import yaml
from dotenv import load_dotenv
from litellm import completion
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.logging import log_and_raise


logger = logging.getLogger(__name__)


class llmRole(Enum):
    SYSTEM = "system"
    USER = "user"


class supportedModels(Enum):
    Gemini = "gemini/gemini-2.5-flash"


class geminiReasoningLevel(Enum):
    LOW = "low"
    HIGH = "high"


class AdvertSourceExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_path: str
    sourced_from: str
    source_type: str | None = None
    comment: str | None = None


class LocationExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str
    country: str
    address: str | None = None
    post_or_zip_code: str | None = None
    gps_coordinates: str | None = None


class ContactDetailsExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    email: str | None = None
    phone_number: str | None = None
    linkedin: str | None = None
    github: str | None = None
    other_links: list[str] | None = None


class AdvertExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    advert_title: str
    advert_description: str
    source: AdvertSourceExtraction
    placement_location: LocationExtraction
    working_pattern: str
    contact_details: ContactDetailsExtraction
    advertStyle: str
    required_skills: list[str] = Field(default_factory=list)
    desired_skills: list[str] = Field(default_factory=list)


class GeminiLLM:
    def request_response(self, model_name: supportedModels, access_role: llmRole, content_struct):
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            msg = "GEMINI_API_KEY is not configured in environment variables"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

        contents = content_struct["text"]
        messages = [{"role": access_role.value, "content": contents}]
        response = completion(
            model=model_name.value,
            messages=messages,
            temperature=0,
        )
        return response

    def build_contents(self, text_input, file_input=None):
        contents = {"file_paths": []}
        if not text_input:
            msg = "No text input was provided"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

        contents["text"] = text_input
        if file_input:
            if not os.path.exists(file_input):
                msg = "The provided source path does not exist"
                log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
            contents["file_paths"].append(file_input)
        return contents

    def get_reply_from_response(self, response):
        return response.choices[0].message.content

    def extract_advert_yaml_from_webpage(
        self,
        webpage_url: str,
        output_yaml_path: str | None = None,
        model_name: supportedModels = supportedModels.Gemini,
        sourced_from: str = "website",
    ) -> tuple[AdvertExtraction, str]:
        webpage_text = self._fetch_webpage_text(webpage_url)
        prompt = self._build_advert_extraction_prompt(webpage_url, sourced_from, webpage_text)
        content_struct = self.build_contents(text_input=prompt)

        response = self.request_response(model_name, llmRole.USER, content_struct)
        raw_reply = self.get_reply_from_response(response)
        if not isinstance(raw_reply, str):
            msg = "Gemini response did not contain text content"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        reply_text = cast(str, raw_reply)
        advert_payload = self._parse_advert_model(reply_text)

        yaml_text = yaml.safe_dump(
            advert_payload.model_dump(),
            sort_keys=False,
            allow_unicode=False,
        )

        if output_yaml_path:
            output_dir = os.path.dirname(output_yaml_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(output_yaml_path, "w", encoding="utf-8") as file:
                file.write(yaml_text)

        return advert_payload, yaml_text

    def _fetch_webpage_text(self, webpage_url: str) -> str:
        try:
            request = Request(
                webpage_url,
                headers={"User-Agent": "Mozilla/5.0 CVBuilder/1.0"},
            )
            with urlopen(request, timeout=30) as response:
                raw_html = response.read().decode("utf-8", errors="replace")
        except (URLError, ValueError, TimeoutError):
            msg = f"Unable to fetch webpage content from {webpage_url}"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

        text_without_script = re.sub(r"<script[\\s\\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
        text_without_style = re.sub(r"<style[\\s\\S]*?</style>", " ", text_without_script, flags=re.IGNORECASE)
        text_without_tags = re.sub(r"<[^>]+>", " ", text_without_style)
        cleaned_text = re.sub(r"\\s+", " ", text_without_tags).strip()

        if not cleaned_text:
            msg = f"No text content extracted from webpage {webpage_url}"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

        return cleaned_text

    def _build_advert_extraction_prompt(self, webpage_url: str, sourced_from: str, webpage_text: str) -> str:
        clipped_text = webpage_text[:30000]
        return (
            "Extract job advert data from the provided webpage text and return ONLY valid JSON. "
            "Do not include markdown, code fences, commentary, or extra keys. "
            "Use this exact object shape: "
            "{"
            '"advert_title": str, '
            '"advert_description": str, '
            '"source": {"source_path": str, "sourced_from": str, "source_type": str|null, "comment": str|null}, '
            '"placement_location": {"city": str, "country": str, "address": str|null, "post_or_zip_code": str|null, "gps_coordinates": str|null}, '
            '"working_pattern": str, '
            '"contact_details": {"name": str, "email": str|null, "phone_number": str|null, "linkedin": str|null, "github": str|null, "other_links": list[str]|null}, '
            '"advertStyle": str, '
            '"required_skills": list[str], '
            '"desired_skills": list[str]'
            "}. "
            "Rules: source.source_path must equal the webpage URL, source.sourced_from must equal the value provided, "
            "missing optional fields must be null, and missing skill lists must be empty lists. "
            f"Webpage URL: {webpage_url}. "
            f"sourced_from: {sourced_from}. "
            f"Webpage text: {clipped_text}"
        )

    def _parse_advert_model(self, raw_reply: str) -> AdvertExtraction:
        candidate_text = raw_reply.strip()

        if candidate_text.startswith("```"):
            candidate_text = re.sub(r"^```(?:json)?", "", candidate_text).strip()
            candidate_text = re.sub(r"```$", "", candidate_text).strip()

        if not candidate_text.startswith("{"):
            start = candidate_text.find("{")
            end = candidate_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate_text = candidate_text[start:end + 1]

        try:
            payload = json.loads(candidate_text)
        except json.JSONDecodeError:
            msg = "Gemini response was not valid JSON"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

        try:
            return AdvertExtraction.model_validate(payload)
        except ValidationError as error:
            msg = f"Gemini response did not match advert schema: {error}"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        raise AssertionError("Unreachable code after log_and_raise")


def test_gemini():
    gemini = GeminiLLM()
    content_struct = gemini.build_contents(
        text_input="count to 5 and then stop",
        file_input=None,
    )
    response = gemini.request_response(
        model_name=supportedModels.Gemini,
        access_role=llmRole.USER,
        content_struct=content_struct,
    )
    reply = gemini.get_reply_from_response(response)
    print("Gemini's reply: ", reply)

def test_advert_extraction():
    
    gemini = GeminiLLM()
    advert_model, advert_yaml = gemini.extract_advert_yaml_from_webpage(
        webpage_url='https://www.reed.co.uk/jobs/systems-and-innovation-manager/56562503?source=searchResults&filter=%2Fjobs%2Fit-jobs',
        output_yaml_path="data/advert_src/extracted_advert.yaml",
        sourced_from="reed.co.uk",
    )

    print(advert_yaml)

if __name__ == "__main__":
    #test_gemini()
    test_advert_extraction()
