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

"""Check the documented boundary between CWL records and MCP arguments."""

from pathlib import Path

import pytest
from cwl_utils.parser import Process, load_document_by_uri
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from pydantic import JsonValue, TypeAdapter

from cwl2mcp.converter import to_mcp_tool

EXAMPLES = Path(__file__).parent / "examples"


def test_eoap_cwl_arguments_need_scalar_adaptation_for_mcp() -> None:
    process = load_document_by_uri((EXAMPLES / "eoap.cwl").resolve().as_uri())
    assert isinstance(process, Process)
    tool = to_mcp_tool(process, "example.org/mcp")
    arguments = TypeAdapter(dict[str, JsonValue]).validate_json(
        (EXAMPLES / "arguments.json").read_text()
    )
    source = arguments["source"]
    timestamp = arguments["timestamp"]
    assert isinstance(source, dict)
    assert isinstance(timestamp, dict)
    adapted = arguments | {"source": source["value"], "timestamp": timestamp["value"]}
    validator = Draft202012Validator(tool.input_schema, format_checker=FormatChecker())
    with pytest.raises(ValidationError):
        validator.validate(arguments)
    validator.validate(adapted)
    assert tool.output_schema is not None
    Draft202012Validator(tool.output_schema, format_checker=FormatChecker()).validate(
        {f"{name}_result": value for name, value in adapted.items()}
    )
