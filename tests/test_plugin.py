from pathlib import Path
from unittest.mock import Mock

import pytest
from cwl_utils.parser.cwl_v1_2 import CommandLineTool
from pydantic import AnyUrl, ValidationError
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    TranspilerContext,
    TranspilerContextResolver,
)
from transpiler_mate.api.software_application_models import SoftwareApplication

from cwl2mcp.plugin import Cwl2McpOptions, cwl2mcp


@pytest.fixture
def context() -> TranspilerContext:
    return TranspilerContext(
        source=AnyUrl("file:///example.cwl"),
        document={"main": CommandLineTool(id="main", inputs=[], outputs=[])},
        metadata=SoftwareApplication.model_construct(),
        resolver=Mock(spec=TranspilerContextResolver),
    )


@pytest.mark.parametrize("process_id", [None, "invalid"])
def test_conversion_failure_preserves_output_and_chains_cause(
    context: TranspilerContext, tmp_path: Path, process_id: str | None
) -> None:
    output = tmp_path / "tools.json"
    output.write_text("existing output", encoding="utf-8")
    context = context.model_copy(
        update={
            "process_id": process_id,
            "document": {
                "first": CommandLineTool(id="first", inputs=[], outputs=[]),
                "invalid": CommandLineTool(id="invalid name", inputs=[], outputs=[]),
            },
        }
    )

    with pytest.raises(PluginFailureError, match="name") as failure:
        cwl2mcp.execute(context, Cwl2McpOptions(output=output))

    assert isinstance(failure.value.__cause__, ValidationError)
    assert output.read_text(encoding="utf-8") == "existing output"


@pytest.mark.parametrize("failure_stage", ["parent", "output"])
def test_write_failure_reports_destination_and_chains_cause(
    context: TranspilerContext, tmp_path: Path, failure_stage: str
) -> None:
    output = tmp_path / "tools.json"
    if failure_stage == "parent":
        output.write_text("blocking file", encoding="utf-8")
        output = output / "nested.json"
    else:
        output.mkdir()

    with pytest.raises(PluginExecutionError, match="Cannot write MCP tools") as failure:
        cwl2mcp.execute(context, Cwl2McpOptions(output=output))

    assert str(output) in str(failure.value)
    assert isinstance(failure.value.__cause__, OSError)


def test_empty_document_writes_empty_mapping(context: TranspilerContext, tmp_path: Path) -> None:
    output = tmp_path / "nested" / "tools.json"

    cwl2mcp.execute(context.model_copy(update={"document": {}}), Cwl2McpOptions(output=output))

    assert output.read_text(encoding="utf-8") == "{}\n"
