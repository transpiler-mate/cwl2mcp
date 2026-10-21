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
from cwl_utils.parser.cwl_v1_2 import CommandLineTool, CommandOutputParameter
from jsonschema import Draft202012Validator

from cwl2mcp.converter import to_mcp_tool


@pytest.mark.parametrize("cwl_type", ["File", "Directory"])
def test_file_outputs_use_cwl2ogc_uri_and_catalog_alternatives(cwl_type: str) -> None:
    process = CommandLineTool(
        id="example",
        inputs=[],
        outputs=[CommandOutputParameter(id="example/report", type_=cwl_type)],
    )
    before = deepcopy(process.save(relative_uris=False))
    tool = to_mcp_tool(process, "example.org/mcp")
    assert tool.output_schema is not None
    Draft202012Validator.check_schema(tool.output_schema)
    alternatives = tool.output_schema["$defs"]["report"]["oneOf"]
    assert {"type": "string", "format": "uri"} in alternatives
    assert {
        "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
    } in alternatives
    assert tool.field_meta == {}
    assert "artifactId" not in str(tool.output_schema)
    assert process.save(relative_uris=False) == before


def test_file_artifact_extensions_do_not_create_receipt_metadata() -> None:
    output = CommandOutputParameter(id="example/report", type_="File")
    process = CommandLineTool(id="example", inputs=[], outputs=[output])
    expected = to_mcp_tool(process, "example.org/mcp")
    output.extension_fields["https://terradue.com/cwl/file-artifacts/v1#mediaType"] = (
        "application/json"
    )
    assert to_mcp_tool(process, "example.org/mcp") == expected
