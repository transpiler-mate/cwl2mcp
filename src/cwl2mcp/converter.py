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

"""Convert parsed CWL processes and their MCP hints into tool definitions."""

import re
from collections.abc import Mapping

from cwl2ogc import BaseCWLtypes2OGCConverter
from cwl_utils.parser import Process
from schema_salad.runtime import LoadingOptions

from .mcp_hint import Tool as ToolHint
from .mcp_tool import McpTool, ToolAnnotations


def to_snake_case(name: str) -> str:
    """Convert a camel-case metadata property name to snake case."""
    # Insert underscore between lowercase/digit and uppercase,
    # and between consecutive uppercase and uppercase+lowercase
    separated_words = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", separated_words).lower()


def _expand_hint_class(hint_class: str, namespaces: Mapping[str, str]) -> str:
    prefix, separator, local_name = hint_class.partition(":")
    if separator and prefix in namespaces:
        return namespaces[prefix] + local_name
    return hint_class


def _load_tool_hint(hint: Mapping[str, object], process: Process) -> ToolHint:
    """Validate a hint while preserving its literal MCP callable name.

    Salad requires the shared ``name`` predicate to use identifier semantics.
    MCP names are literal strings, so retain the validated input spelling
    instead of the URI that Salad expands relative to the CWL process.
    """
    tool_hint = ToolHint.fromDoc(
        hint,
        process.id,
        LoadingOptions(
            namespaces=dict(process.loadingOptions.namespaces),
            fileuri=process.loadingOptions.fileuri,
            # A callable name does not refer to another CWL document object.
            no_link_check=True,
        ),
    )
    name = hint.get("name")
    if isinstance(name, str):
        tool_hint.name = name
    return tool_hint


def get_tool_hint(process: Process) -> ToolHint | None:
    """Load the first MCP Tool hint from a parsed CWL process.

    Already parsed Tool hints are returned unchanged. Extension mappings are
    matched by their full class URI or a prefix declared by the process.

    Returns:
        The matching hint, or None when the process has no MCP Tool hint.

    Raises:
        schema_salad.exceptions.ValidationException: If a matching mapping
            does not conform to the hint schema.
    """
    namespaces = process.loadingOptions.namespaces
    for hint in process.hints or []:
        if isinstance(hint, ToolHint):
            return hint
        if not isinstance(hint, Mapping):
            continue
        hint_class = hint.get("class")
        if not isinstance(hint_class, str):
            continue
        if (
            _expand_hint_class(hint_class, namespaces)
            == "https://eoap.github.io/cwl-mcp-extension#Tool"
        ):
            return _load_tool_hint(hint, process)
    return None


def to_mcp_tool(process: Process, meta_prefix: str) -> McpTool:
    """Convert a process, using its optional MCP hint for tool metadata.

    Args:
        process: Parsed CWL process to expose as a tool.
        meta_prefix: Prefix for custom MCP metadata keys.

    Raises:
        schema_salad.exceptions.ValidationException: If the MCP hint is invalid.
    """
    tool_hint = get_tool_hint(process)
    converter = BaseCWLtypes2OGCConverter(process)

    return McpTool(
        name=tool_hint.name if tool_hint and tool_hint.name else process.id,
        title=tool_hint.title if tool_hint and tool_hint.title else process.label or None,
        description=process.doc if process.doc else None,
        input_schema=dict(converter.get_inputs_json_schema()),
        output_schema=dict(converter.get_outputs_json_schema()),
        annotations=ToolAnnotations(
            read_only_hint=tool_hint.annotations.readOnlyHint,
            destructive_hint=tool_hint.annotations.destructiveHint,
            idempotent_hint=tool_hint.annotations.idempotentHint,
            open_world_hint=tool_hint.annotations.openWorldHint,
        )
        if tool_hint and tool_hint.annotations
        else None,
        field_meta={
            f"{meta_prefix}-{to_snake_case(property_name)}": property_value
            for property_name in ("aliases", "useWhen", "doNotUseWhen")
            if (property_value := getattr(tool_hint, property_name, None))
        },
    )
