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

"""Exercise installed runtime/plugin discovery against the documented EOAP example.

The example imports canonical EOAP schemas over HTTPS, so these integration
tests require network access (or an already populated CWL loader cache).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from pydantic import JsonValue, TypeAdapter
from ruamel.yaml import YAML

EXAMPLES = Path(__file__).parent / "examples"
ROOT = Path(__file__).parents[1]
JSON_OBJECT = TypeAdapter(dict[str, JsonValue])


def _object(value: JsonValue) -> dict[str, JsonValue]:
    assert isinstance(value, dict)
    return value


@pytest.fixture(scope="module", params=["#main", ""], ids=["selected", "document"])
def exported_tool(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> dict[str, JsonValue]:
    output = tmp_path_factory.mktemp("runtime-crosswalk") / "nested" / "tools.json"
    command = [
        sys.executable,
        "-c",
        "from transpiler_mate.runtime.cli import main; main()",
        "cwl2mcp",
        "--output",
        str(output),
        f"{EXAMPLES / 'eoap.cwl'}{request.param}",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    serialized = output.read_text(encoding="utf-8")
    exported = JSON_OBJECT.validate_json(serialized)
    assert serialized == json.dumps(exported, indent=2, sort_keys=True) + "\n"
    repeated = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    assert output.read_text(encoding="utf-8") == serialized
    if request.param:
        return exported
    assert set(exported) == {"main"}
    return _object(exported["main"])


def test_runtime_output_conforms_to_mcp_schema(exported_tool: dict[str, JsonValue]) -> None:
    schema = YAML(typ="safe").load(ROOT / "schemas" / "mcp-tool.yaml")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(exported_tool)


def test_runtime_metadata_matches_crosswalk(exported_tool: dict[str, JsonValue]) -> None:
    assert exported_tool["name"] == "inspect_source"
    assert exported_tool["title"] == "Inspect Source"
    assert exported_tool["description"] == (
        "Return a source URI, timestamp and GeoJSON point without changing their records."
    )
    assert exported_tool["annotations"] == {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
    assert exported_tool["_meta"] == {
        "io.github.transpiler-mate/cwl2mcp-aliases": ["inspect a spatial source"],
        "io.github.transpiler-mate/cwl2mcp-use_when": "the user needs to inspect a spatial source.",
        "io.github.transpiler-mate/cwl2mcp-do_not_use_when": "the user needs data modification.",
    }


def test_runtime_schemas_match_eoap_projection(exported_tool: dict[str, JsonValue]) -> None:
    arguments = JSON_OBJECT.validate_json((EXAMPLES / "arguments.json").read_text())
    source = _object(arguments["source"])
    timestamp = _object(arguments["timestamp"])
    arguments = arguments | {"source": source["value"], "timestamp": timestamp["value"]}
    input_schema = _object(exported_tool["inputSchema"])
    output_schema = _object(exported_tool["outputSchema"])
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator.check_schema(output_schema)
    validator = Draft202012Validator(input_schema, format_checker=FormatChecker())
    validator.validate(arguments)
    Draft202012Validator(output_schema, format_checker=FormatChecker()).validate(
        {f"{name}_result": value for name, value in arguments.items()}
    )
    definitions = _object(input_schema["$defs"])
    assert definitions["source"] == {"type": "string", "format": "uri"}
    assert definitions["timestamp"] == {"type": "string", "format": "date-time"}
    invalid_arguments = [
        arguments | {"source": {"value": "https://example.org/data.tif"}},
        arguments | {"point": {"type": "Point", "coordinates": [12.5, 41.9]}},
        arguments | {"timestamp": "not a date"},
        arguments | {"source": "not a URI"},
    ]
    for invalid in invalid_arguments:
        with pytest.raises(ValidationError):
            validator.validate(invalid)
