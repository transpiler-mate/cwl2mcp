# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from copy import deepcopy

import pytest
from cwl_utils.parser.cwl_v1_2 import CommandInputParameter, CommandLineTool
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as SchemaValidationError
from pydantic import ValidationError
from schema_salad.exceptions import ValidationException

from cwl2mcp.converter import to_mcp_tool
from cwl2mcp.mcp_hint import Annotations, Tool


def _process() -> CommandLineTool:
    return CommandLineTool(id="example", inputs=[], outputs=[], label="CWL title", doc="CWL doc")


def _hint(name: str = "override") -> Tool:
    return Tool(
        name,
        ["alias"],
        "needed",
        "unnecessary",
        Annotations(False, False, False, False),
        title="Explicit",
    )


def test_metadata_precedence_prefix_aliases_and_false_hints() -> None:
    process = _process()
    process.hints = [_hint()]
    before = deepcopy(process.save(relative_uris=False))

    tool = to_mcp_tool(process, "example.org/mcp").model_dump(by_alias=True, exclude_none=True)

    assert tool["name"] == "override"
    assert tool["title"] == "Explicit"
    assert tool["description"] == "CWL doc"
    assert tool["_meta"] == {
        "example.org/mcp-aliases": ["alias"],
        "example.org/mcp-use-when": "needed",
        "example.org/mcp-do-not-use-when": "unnecessary",
    }
    assert tool["annotations"] == dict.fromkeys(
        ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"], False
    )
    assert process.save(relative_uris=False) == before


def test_absent_hint_uses_process_metadata_without_inventing_annotations() -> None:
    tool = to_mcp_tool(_process(), "example.org/mcp")
    assert tool.name == "example"
    assert tool.title == "CWL title"
    assert tool.description == "CWL doc"
    assert tool.annotations is None
    assert tool.field_meta == {}


def test_empty_guidance_is_omitted() -> None:
    process = _process()
    process.hints = [Tool("tool", [], "", "", Annotations(True, False, True, False))]
    assert to_mcp_tool(process, "example.org/mcp").field_meta == {}


def test_missing_label_and_doc_are_omitted() -> None:
    process = CommandLineTool(id="example", inputs=[], outputs=[])
    result = to_mcp_tool(process, "example.org/mcp").model_dump(exclude_none=True)
    assert "title" not in result
    assert "description" not in result


def test_first_matching_hint_wins() -> None:
    process = _process()
    process.hints = [_hint("first"), _hint("second")]
    assert to_mcp_tool(process, "example.org/mcp").name == "first"


def test_tool_requirement_is_not_used_as_hint() -> None:
    process = _process()
    process.requirements = [_hint()]
    assert to_mcp_tool(process, "example.org/mcp").name == "example"


@pytest.mark.parametrize("name", ["contains spaces", "https://example.org/tool", "x" * 129])
def test_invalid_callable_name_is_rejected(name: str) -> None:
    process = _process()
    process.hints = [_hint(name)]
    with pytest.raises(ValidationError, match="name"):
        to_mcp_tool(process, "example.org/mcp")


def test_documentation_paragraphs_are_not_silently_coerced() -> None:
    process = _process()
    process.doc = ["First.", "Second."]
    with pytest.raises(ValidationError, match="description"):
        to_mcp_tool(process, "example.org/mcp")


def test_unknown_hint_field_is_rejected() -> None:
    process = _process()
    hint = _hint().save()
    hint["class"] = "https://eoap.github.io/cwl-mcp-extension#Tool"
    hint["description"] = "Unsupported override"
    process.hints = [hint]
    with pytest.raises(ValidationException, match="invalid field `description`"):
        to_mcp_tool(process, "example.org/mcp")


@pytest.mark.parametrize(
    ("cwl_type", "valid", "invalid"),
    [("string", "text", 1), ("boolean", False, "false"), ("int", 42, "42")],
)
def test_generated_input_schema_enforces_primitive_types(
    cwl_type: str, valid: str | bool | int, invalid: str | int
) -> None:
    process = _process()
    process.inputs = [CommandInputParameter(id="example/value", type_=cwl_type)]
    schema = to_mcp_tool(process, "example.org/mcp").input_schema
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    validator.validate({"value": valid})
    with pytest.raises(SchemaValidationError):
        validator.validate({"value": invalid})
    with pytest.raises(SchemaValidationError):
        validator.validate({})


def test_repeated_conversion_is_deterministic() -> None:
    process = _process()
    assert to_mcp_tool(process, "example.org/mcp") == to_mcp_tool(process, "example.org/mcp")
