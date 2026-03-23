import os
import logging
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

import yaml
from src.logging import log_and_raise


logger = logging.getLogger(__name__)


def _normalize_for_yaml(value: Any) -> Any:
    """Convert dataclass objects and non-YAML-native values into YAML-safe structures."""
    if is_dataclass(value) and not isinstance(value, type):
        normalized = {}
        for dataclass_field in fields(value):
            normalized[dataclass_field.name] = _normalize_for_yaml(getattr(value, dataclass_field.name))
        return normalized

    type_handlers = {
        Enum: lambda item: item.value,
        datetime: lambda item: item.strftime("%d-%m-%Y"),
        date: lambda item: item.strftime("%d-%m-%Y"),
        dict: lambda item: {key: _normalize_for_yaml(entry) for key, entry in item.items()},
        list: lambda item: [_normalize_for_yaml(entry) for entry in item],
        tuple: lambda item: [_normalize_for_yaml(entry) for entry in item],
        set: lambda item: sorted([_normalize_for_yaml(entry) for entry in item], key=str),
    }

    for value_type, handler in type_handlers.items():
        if isinstance(value, value_type):
            return handler(value)

    return value


def schema_object_to_yaml_dict(schema_object: Any) -> dict[str, Any]:
    """Serialize a schema dataclass object into a YAML-safe dictionary."""
    if not is_dataclass(schema_object) or isinstance(schema_object, type):
        msg = "schema_object must be a dataclass instance"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))
    return _normalize_for_yaml(schema_object)


def export_schema_objects_to_yaml(
    schema_objects: Any,
    output_file_path: str,
    use_multi_document: bool = True,
) -> str:
    """Export one or many schema dataclass objects to a YAML file."""
    if schema_objects is None:
        msg = "schema_objects cannot be None"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

    if isinstance(schema_objects, (list, tuple, set)):
        object_list = list(schema_objects)
    else:
        object_list = [schema_objects]

    if not object_list:
        msg = "schema_objects cannot be empty"
        log_and_raise(logger, logging.ERROR, msg, ValueError(msg))

    normalized_objects = [schema_object_to_yaml_dict(item) for item in object_list]

    output_directory = os.path.dirname(output_file_path)
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    with open(output_file_path, "w", encoding="utf-8") as file:
        if use_multi_document and len(normalized_objects) > 1:
            yaml.safe_dump_all(
                normalized_objects,
                file,
                sort_keys=False,
                allow_unicode=False,
            )
        else:
            payload = normalized_objects if len(normalized_objects) > 1 else normalized_objects[0]
            yaml.safe_dump(
                payload,
                file,
                sort_keys=False,
                allow_unicode=False,
            )

    return output_file_path
