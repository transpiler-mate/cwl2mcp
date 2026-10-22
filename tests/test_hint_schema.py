import pytest
from cwl_utils.parser.cwl_v1_2 import CommandLineTool
from pydantic import JsonValue
from schema_salad.exceptions import ValidationException

from cwl2mcp.converter import get_tool_hint, to_mcp_tool
from cwl2mcp.mcp_hint import Annotations


def _process(title: JsonValue) -> CommandLineTool:
    return CommandLineTool(
        id="file:///example.cwl#main",
        inputs=[],
        outputs=[],
        label="Process label",
        hints=[
            {
                "class": "https://eoap.github.io/cwl-mcp-extension#Tool",
                "name": "inspect_source",
                "title": title,
                "aliases": [],
                "useWhen": "Inspection is needed.",
                "doNotUseWhen": "Modification is needed.",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False,
                },
            }
        ],
    )


def test_title_and_annotations_load_without_nested_discriminator() -> None:
    hint = get_tool_hint(_process("Inspect Source"))

    assert hint is not None
    assert hint.name == "inspect_source"
    assert hint.title == "Inspect Source"
    assert isinstance(hint.annotations, Annotations)
    assert hint.annotations.destructiveHint is False


def test_hint_title_overrides_process_label_in_mcp_output() -> None:
    tool = to_mcp_tool(_process("Inspect Source"), "example.org/mcp")

    assert tool.name == "inspect_source"
    assert tool.title == "Inspect Source"


def test_rejects_non_string_title() -> None:
    with pytest.raises(ValidationException, match="title"):
        get_tool_hint(_process(123))


@pytest.mark.parametrize("field", ["name", "aliases", "useWhen", "doNotUseWhen", "annotations"])
def test_rejects_missing_required_hint_fields(field: str) -> None:
    process = _process("Inspect Source")
    assert process.hints is not None
    del process.hints[0][field]

    with pytest.raises(ValidationException, match=field):
        get_tool_hint(process)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", 123),
        ("aliases", "single alias"),
        ("aliases", [123]),
        ("useWhen", False),
        ("doNotUseWhen", []),
        ("annotations", "not annotations"),
    ],
)
def test_rejects_invalid_hint_field_types(field: str, value: JsonValue) -> None:
    process = _process("Inspect Source")
    assert process.hints is not None
    process.hints[0][field] = value

    with pytest.raises(ValidationException, match=field):
        get_tool_hint(process)


@pytest.mark.parametrize(
    "field", ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]
)
@pytest.mark.parametrize("value", [None, "true", 1])
def test_rejects_missing_or_non_boolean_annotations(field: str, value: JsonValue) -> None:
    process = _process("Inspect Source")
    assert process.hints is not None
    process.hints[0]["annotations"][field] = value

    with pytest.raises(ValidationException, match=field):
        get_tool_hint(process)
