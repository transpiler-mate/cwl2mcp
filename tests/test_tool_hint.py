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
from cwl_utils.parser import LoadingOptions, Process, load_document_by_yaml
from pydantic import JsonValue
from schema_salad.exceptions import ValidationException

from cwl2mcp.converter import get_tool_hint
from cwl2mcp.mcp_hint import Annotations, Tool


def _process(hints: list[JsonValue]) -> Process:
    process = load_document_by_yaml(
        {
            "cwlVersion": "v1.2",
            "class": "CommandLineTool",
            "id": "example",
            "inputs": {},
            "outputs": {},
            "$namespaces": {"agent": "https://eoap.github.io/cwl-mcp-extension#"},
            "hints": hints,
        },
        "file:///test.cwl",
        LoadingOptions(no_link_check=True),
    )
    assert isinstance(process, Process)
    return process


@pytest.mark.parametrize(
    "hint_class", ["agent:Tool", "https://eoap.github.io/cwl-mcp-extension#Tool"]
)
def test_loads_tool_hint_without_mutating_process(hint_class: str) -> None:
    process = _process(
        [
            {"class": "https://example.org/Other"},
            {
                "class": hint_class,
                "name": "tool",
                "aliases": ["alias"],
                "useWhen": "needed",
                "doNotUseWhen": "unnecessary",
                "annotations": {
                    "class": "Annotations",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False,
                },
            },
        ]
    )
    before = deepcopy(process.hints)

    hint = get_tool_hint(process)

    assert isinstance(hint, Tool)
    assert hint.aliases == ["alias"]
    assert isinstance(hint.annotations, Annotations)
    assert hint.annotations.destructiveHint is False
    assert process.hints == before


@pytest.mark.parametrize("hints", [[], [{"class": "https://example.org/Tool"}]])
def test_returns_none_without_matching_hint(hints: list[JsonValue]) -> None:
    assert get_tool_hint(_process(hints)) is None


def test_returns_existing_tool_hint() -> None:
    hint = Tool("tool", [], "needed", "unnecessary", Annotations(True, False, True, False))
    process = _process([])
    process.hints = [hint]

    assert get_tool_hint(process) is hint


def test_rejects_malformed_matching_hint() -> None:
    with pytest.raises(ValidationException, match="missing required field `aliases`"):
        get_tool_hint(_process([{"class": "agent:Tool", "name": "tool"}]))


@pytest.mark.parametrize(
    "unrelated_hint",
    [None, "not a mapping", {}, {"class": None}, {"class": 42}, {"class": "unknown:Tool"}],
)
def test_skips_unrelated_hints_before_matching_tool(unrelated_hint: JsonValue) -> None:
    process = _process([])
    hint = Tool("tool", [], "needed", "unnecessary", Annotations(True, False, True, False))
    process.hints = [unrelated_hint, hint]

    assert get_tool_hint(process) is hint


def test_expands_process_namespace_for_mapping_hint() -> None:
    process = _process([])
    process.hints = [
        {
            "class": "agent:Tool",
            "name": "literal_name",
            "aliases": [],
            "useWhen": "needed",
            "doNotUseWhen": "unnecessary",
            "annotations": {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            },
        }
    ]

    hint = get_tool_hint(process)

    assert hint is not None
    assert hint.name == "literal_name"
    assert hint.title is None
