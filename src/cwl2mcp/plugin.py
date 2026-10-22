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

"""Transpiler Mate entry point using the runtime's resolved CWL context."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    TranspilerContext,
    transpiler_plugin,
)

from cwl2mcp.converter import to_mcp_tool_dict


class Cwl2McpOptions(BaseModel):
    """Output destination exposed as a runtime CLI option."""

    model_config = ConfigDict(extra="forbid")
    output: Path = Field(default=Path("tools.json"), description="Output JSON file path")
    meta_prefix: str = Field(
        default="io.github.transpiler-mate/cwl2mcp", description="The '_meta' property prefix"
    )


@transpiler_plugin(
    name="cwl2mcp",
    description="Derive MCP tool definitions from CWL processes.",
    options_model=Cwl2McpOptions,
)
def cwl2mcp(context: TranspilerContext, options: Cwl2McpOptions) -> None:
    """Write one selected Tool or a process-ID mapping for the whole document.

    Parent directories are created. Existing output is replaced only after all
    processes have been converted successfully.

    Raises:
        PluginFailureError: If a CWL contract cannot be converted.
        PluginExecutionError: If writing the output fails.
    """
    try:
        if context.process_id:
            data = to_mcp_tool_dict(context.resolved_process, options.meta_prefix)
        else:
            data = {
                process_id: to_mcp_tool_dict(process, options.meta_prefix)
                for process_id, process in sorted(context.document.items())
            }
    except ValueError as error:
        raise PluginFailureError(str(error)) from error
    try:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except OSError as error:
        raise PluginExecutionError(
            f"Cannot write MCP tools to {options.output}: {error}"
        ) from error
