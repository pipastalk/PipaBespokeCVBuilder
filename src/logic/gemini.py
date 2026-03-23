import json
import logging
import os
import re
from enum import Enum
from typing import Any, cast
from urllib.error import URLError
from urllib.request import Request, urlopen

import yaml
from dotenv import load_dotenv
from litellm import completion
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.logic.data_tools import get_multi_skill_related_context, get_skill_related_context, search_user_skills
from src.models.User import User
from src.models.schema import Advert, Skill
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
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    linkedin: str | None = None
    github: str | None = None
    other_links: list[str] | None = None


class AdvertExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    advert_title: str
    source: AdvertSourceExtraction
    placement_location: LocationExtraction
    working_pattern: str
    contact_details: ContactDetailsExtraction
    advertStyle: str
    required_skills: list[str] = Field(default_factory=list)
    desired_skills: list[str] = Field(default_factory=list)
    advert_description: str


class GeminiLLM:
    def _get_advert_skill_names(self, skills: set[str] | set[Skill]) -> list[str]:
        extracted: list[str] = []
        for item in skills or set():
            if isinstance(item, Skill):
                extracted.append(item.name)
            elif isinstance(item, str):
                extracted.append(item)
            else:
                extracted.append(str(item))
        return sorted(extracted)

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
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg, request, raw_html))

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
            "Extract job advert data from the provided webpage text and return ONLY valid JSON.  "
            "Do not include markdown, code fences, commentary, or extra keys. "
            "Review if the advert is formal, informal, or a hybrid and set advertStyle accordingly."
            "Put the original advert text in the advert_description field. "
            "Extract any skillsets mentioned in the job and fill required_skills and desired_skills accordingly. "
            "Use this exact object shape: "
            "{"
            '"advert_title": str, '
            '"source": {"source_path": str, "sourced_from": str, "source_type": str|null, "comment": str|null}, '
            '"placement_location": {"city": str, "country": str, "address": str|null, "post_or_zip_code": str|null, "gps_coordinates": str|null}, '
            '"working_pattern": str, '
            '"contact_details": {"name": str|null, "email": str|null, "phone_number": str|null, "linkedin": str|null, "github": str|null, "other_links": list[str]|null}, '
            '"advertStyle": str, '
            '"required_skills": list[str], '
            '"desired_skills": list[str], '
            '"advert_description": str '
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
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg, candidate_text))

        try:
            return AdvertExtraction.model_validate(payload)
        except ValidationError as error:
            msg = f"Gemini response did not match advert schema: {error}"
            log_and_raise(logger, logging.ERROR, msg, ValueError(msg, candidate_text))
        raise AssertionError("Unreachable code after log_and_raise")

    def generate_tailored_cv(
        self,
        user: User,
        advert: Advert,
        model_name: supportedModels = supportedModels.Gemini,
        max_tool_rounds: int = 6,
    ) -> str:
        skill_match_summary = search_user_skills(user, advert)
        system_prompt = self._build_cv_builder_system_prompt()
        user_prompt = self._build_tailored_cv_prompt(advert, skill_match_summary)

        tools: list[dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "search_user_skills",
                    "description": (
                        "Return advert-to-user skill matches and unmatched skills. "
                        "Use this first to identify strongest overlap with the role."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_skill_related_context",
                    "description": (
                        "Get projects, placements, qualifications, and hobbies linked to a user skill id."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_id": {
                                "type": "string",
                            }
                        },
                        "required": ["skill_id"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_multi_skill_related_context",
                    "description": "Get related project/placement/qualification/hobby context for many skill ids.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            }
                        },
                        "required": ["skill_ids"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

        messages: list[dict[str, Any]] = [
            {"role": llmRole.SYSTEM.value, "content": system_prompt},
            {"role": llmRole.USER.value, "content": user_prompt},
        ]

        for _ in range(max_tool_rounds):
            response = completion(
                model=model_name.value,
                messages=messages,
                tools=tools,
                temperature=0,
            )
            response_message = cast(Any, response).choices[0].message
            assistant_message = self._to_assistant_message_dict(response_message)
            messages.append(assistant_message)

            tool_calls = self._extract_tool_calls(response_message)
            if not tool_calls:
                content = assistant_message.get("content")
                if isinstance(content, str) and content.strip():
                    return content
                break

            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_call_id = tool_call["id"]
                raw_args = tool_call["arguments"]
                try:
                    parsed_args = json.loads(raw_args) if raw_args else {}
                except json.JSONDecodeError:
                    parsed_args = {}

                tool_result = self._execute_cv_builder_tool(
                    tool_name=tool_name,
                    args=parsed_args,
                    user=user,
                    advert=advert,
                    precomputed_skill_matches=skill_match_summary,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps(tool_result, default=str),
                    }
                )

        msg = "The model did not return final CV output within the allowed tool-call rounds"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
        raise AssertionError("Unreachable code after log_and_raise")

    def _build_cv_builder_system_prompt(self) -> str:
        return (
            "You are an expert CV writer. Build a targeted CV for the provided role using only the supplied data and tool results. "
            "Use tools to gather evidence from skill-linked projects, placements, qualifications, and hobbies before finalizing. "
            "Do not invent facts, companies, achievements, dates, or technologies not present in tool outputs. "
            "Output plain markdown CV sections only."
        )

    def _build_tailored_cv_prompt(self, advert: Advert, skill_match_summary: dict[str, Any]) -> str:
        advert_data = {
            "advert_title": advert.advert_title,
            "advert_description": advert.advert_description,
            "working_pattern": advert.working_pattern,
            "required_skills": self._get_advert_skill_names(advert.required_skills),
            "desired_skills": self._get_advert_skill_names(advert.desired_skills),
            "placement_location": {
                "city": advert.placement_location.city,
                "country": advert.placement_location.country,
            },
            "advert_style": str(advert.advertStyle),
        }
        return (
            "Use the advert details and skill match snapshot to draft a tailored CV. "
            "Before final output, call tools to inspect related context for the best matching skills. "
            "Include sections: Professional Summary, Core Skills, Relevant Experience, Projects, Qualifications, and Additional Evidence.\n\n"
            f"Advert data:\n{json.dumps(advert_data, indent=2, default=str)}\n\n"
            f"Initial skill match snapshot:\n{json.dumps(skill_match_summary, indent=2, default=str)}"
        )

    def _execute_cv_builder_tool(
        self,
        tool_name: str,
        args: dict[str, Any],
        user: User,
        advert: Advert,
        precomputed_skill_matches: dict[str, Any],
    ) -> dict[str, Any]:
        if tool_name == "search_user_skills":
            return precomputed_skill_matches
        if tool_name == "get_skill_related_context":
            skill_id = args.get("skill_id")
            if not isinstance(skill_id, str) or not skill_id.strip():
                raise ValueError("skill_id must be provided as a non-empty string")
            return get_skill_related_context(user, skill_id)
        if tool_name == "get_multi_skill_related_context":
            skill_ids = args.get("skill_ids")
            if not isinstance(skill_ids, list) or not all(isinstance(item, str) for item in skill_ids):
                raise ValueError("skill_ids must be a list of strings")
            return get_multi_skill_related_context(user, skill_ids)

        if tool_name == "advert_skills":
            return {
                "required_skills": self._get_advert_skill_names(advert.required_skills),
                "desired_skills": self._get_advert_skill_names(advert.desired_skills),
            }
        raise ValueError(f"Unsupported tool requested: {tool_name}")

    def _to_assistant_message_dict(self, response_message: Any) -> dict[str, Any]:
        content = getattr(response_message, "content", None)
        tool_calls = self._extract_tool_calls(response_message)

        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": content or "",
        }

        if tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tool_call["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                    },
                }
                for tool_call in tool_calls
            ]
        return assistant_message

    def _extract_tool_calls(self, response_message: Any) -> list[dict[str, str]]:
        raw_tool_calls = getattr(response_message, "tool_calls", None)
        if not raw_tool_calls:
            return []

        extracted_tool_calls: list[dict[str, str]] = []
        for raw_tool_call in raw_tool_calls:
            function_data = getattr(raw_tool_call, "function", None)
            if not function_data:
                continue

            tool_name = getattr(function_data, "name", None)
            tool_arguments = getattr(function_data, "arguments", "{}")
            tool_call_id = getattr(raw_tool_call, "id", None)

            if not isinstance(tool_name, str) or not isinstance(tool_call_id, str):
                continue
            if not isinstance(tool_arguments, str):
                tool_arguments = "{}"

            extracted_tool_calls.append(
                {
                    "id": tool_call_id,
                    "name": tool_name,
                    "arguments": tool_arguments,
                }
            )
        return extracted_tool_calls


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
        webpage_url='https://www.reed.co.uk/jobs/senior-bi-analyst/56690214?source=searchResults&filter=%2Fjobs%2Fit-jobs',
        output_yaml_path="data/advert_src/1.yaml",
        sourced_from="reed.co.uk",
    )
    print(advert_yaml)

if __name__ == "__main__":
    #test_gemini()
    test_advert_extraction()
