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

import json
from importlib.metadata import entry_points
from pathlib import Path

import pytest
from click.testing import CliRunner
from transpiler_mate.runtime.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_plugin_entry_point_is_discovered() -> None:
    entry = next(
        entry for entry in entry_points(group="transpiler_mate.plugins") if entry.name == "cwl2mcp"
    )
    assert entry.load().name == "cwl2mcp"


@pytest.mark.parametrize("selection", ["main", "echo", "expression"])
def test_selected_process_cli(tmp_path: Path, selection: str) -> None:
    output = tmp_path / "nested/tool.json"
    result = CliRunner().invoke(
        main,
        [
            "cwl2mcp",
            "--output",
            str(output),
            f"{FIXTURES / 'graph.cwl'}#{selection}",
        ],
    )
    assert result.exit_code == 0, result.output
    tool = json.loads(output.read_text())
    assert tool["name"] == selection
    assert tool["inputSchema"]["properties"]["region"] == {"$ref": "#/$defs/region"}
    assert tool["inputSchema"]["$defs"]["region"] == {"type": "string"}


def test_document_cli_includes_every_process_and_is_deterministic(
    tmp_path: Path,
) -> None:
    output = tmp_path / "tools.json"
    args = ["cwl2mcp", "--output", str(output), str(FIXTURES / "graph.cwl")]
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    first = output.read_bytes()
    tools = json.loads(first)
    assert set(tools) == {"main", "echo", "expression"}
    assert all(tool["inputSchema"]["type"] == "object" for tool in tools.values())
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    assert output.read_bytes() == first


def test_unknown_process_cli_preserves_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "tool.json"
    output.write_text("existing")
    result = CliRunner().invoke(
        main,
        [
            "cwl2mcp",
            "--output",
            str(output),
            f"{FIXTURES / 'graph.cwl'}#missing",
        ],
    )
    assert result.exit_code != 0
    assert output.read_text() == "existing"


def test_write_failure_is_reported(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        [
            "cwl2mcp",
            "--output",
            str(tmp_path),
            f"{FIXTURES / 'graph.cwl'}#main",
        ],
    )
    assert result.exit_code != 0
