# CWL to MCP crosswalk

This page describes the current [converter](../../src/cwl2mcp/converter.py) and
[export plugin](../../src/cwl2mcp/plugin.py). The plugin generates Tool definitions;
it does not execute CWL, provide an MCP server, or generate artifact receipts.

## Process fields

| CWL source | Resulting JSON | Current mapping |
|---|---|---|
| Nonempty `mcp:Tool.name`, otherwise process `id` | `name` | A mapping hint's literal name is preserved. The fallback process ID is not normalized. |
| Nonempty `mcp:Tool.title`, otherwise `label` | `title` | Omitted when neither supplies a nonempty value. |
| Nonempty process `doc` | `description` | Passed directly to the model. There is no hint description override or appended guidance. |
| `inputs` | `inputSchema` | Result of `BaseCWLtypes2OGCConverter.get_inputs_json_schema()`. |
| `outputs` | `outputSchema` | Result of `BaseCWLtypes2OGCConverter.get_outputs_json_schema()`. |
| `mcp:Tool.annotations` | `annotations` | Copies all four behavioral booleans, including `false`. Omitted when no hint is found. |
| Nonempty `mcp:Tool.aliases` | `_meta["<prefix>-aliases"]` | Preserves the list. |
| Nonempty `mcp:Tool.useWhen` | `_meta["<prefix>-use_when"]` | Preserves the string without changing `description`. |
| Nonempty `mcp:Tool.doNotUseWhen` | `_meta["<prefix>-do_not_use_when"]` | Preserves the string without changing `description`. |

The default prefix is `transpiler-mate.github.io/cwl2mcp`; configure it with
`--meta-prefix`. The converter always supplies `_meta`, even when it is `{}`.
See [output configuration](../how-to/configure-output.md).

The generated [MCP model](../../src/cwl2mcp/mcp_tool.py) requires a name of 1–128
ASCII letters, digits, underscores, dots, or hyphens. A URI-valued fallback ID can
therefore fail validation. Supply an explicit callable name in the hint.
`description` must be a string; lists of CWL documentation paragraphs are not
joined by the converter and can fail model validation.

## Hint selection and validation

Only `process.hints` is searched. The first matching Tool is used; later matches
are not rejected. `requirements` is not searched for MCP hints. Class names may
be full URIs or use any process namespace prefix bound to
`https://eoap.github.io/cwl-mcp-extension#`.

A complete hint for the [EOAP example](../../tests/examples/eoap.cwl) is:

```yaml
hints:
  agent:Tool:
    name: inspect_source
    title: Inspect Source
    aliases: [inspect a spatial source]
    useWhen: the user needs to inspect a spatial source.
    doNotUseWhen: the user needs data modification.
    annotations:
      readOnlyHint: true
      destructiveHint: false
      idempotentHint: true
      openWorldHint: false
```

The document must bind `agent` to the extension namespace. See the
[hint source schema](../../schemas/hints.yaml) and
[generated hint reference](hints_schema.html) for field definitions.
`title` is optional. `aliases`, `useWhen`, `doNotUseWhen`, `annotations`, and all
four annotation booleans are required by the current mapping loader; empty
aliases/guidance values are allowed but omitted from `_meta`. The schema declares
`name` as an identifier string; Salad can synthesize a missing identifier, so an
explicit MCP-compatible name should always be provided.

`annotations.class` may be omitted. If supplied, it must identify `Annotations`.
`Tool.description` is not a declared hint field and is rejected. Unknown
unqualified fields and invalid field values raise validation errors. Already
constructed Tool instances are returned unchanged rather than revalidated.

## Parameter schemas and EOAP conversion

The project pins `cwl2ogc` in [pyproject.toml](../../pyproject.toml). Its schemas
are copied directly into the Tool; this plugin does not add parameter titles,
join parameter documentation, register extra formats, or provide a custom File
receipt schema. Inspect the emitted schema for the resulting types, defaults,
required fields, and definitions.

For the current EOAP example, the input schema contains definitions equivalent
to these excerpts:

```json
{
  "source": {"type": "string", "format": "uri"},
  "timestamp": {"type": "string", "format": "date-time"}
}
```

Properties refer to them through `$ref` values such as `#/$defs/source`.
URI and DateTime records are flattened into scalar strings. The GeoJSON Point
remains an object requiring `type`, `coordinates`, and `bbox`. Its coordinate and
bounding-box values are arrays of numbers. The output schema uses corresponding
`source_result`, `timestamp_result`, and `point_result` fields.

Thus the [CWL arguments fixture](../../tests/examples/arguments.json), which
wraps URI and timestamp values in `{"value": ...}`, needs adaptation before it
can satisfy the exported MCP input schema. See the
[tutorial](../tutorials/first-steps.md) for a matching MCP argument object.
Format validation requires a format-aware JSON Schema validator.

## Example metadata output

The EOAP example produces this metadata excerpt, alongside its input and output
schemas:

```json
{
  "name": "inspect_source",
  "title": "Inspect Source",
  "description": "Return a source URI, timestamp and GeoJSON point without changing their records.",
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false,
    "idempotentHint": true,
    "openWorldHint": false
  },
  "_meta": {
    "transpiler-mate.github.io/cwl2mcp-aliases": ["inspect a spatial source"],
    "transpiler-mate.github.io/cwl2mcp-use_when": "the user needs to inspect a spatial source.",
    "transpiler-mate.github.io/cwl2mcp-do_not_use_when": "the user needs data modification."
  }
}
```

## Export container

| CLI source | Export |
|---|---|
| `tests/examples/eoap.cwl#main` | One MCP Tool object. |
| `tests/examples/eoap.cwl` | A mapping such as `{"main": <Tool>}`. |

JSON aliases are used and fields whose value is `None` are omitted. Keys are
sorted, indentation is two spaces, and output ends with a newline. The plugin
creates parent directories and completes conversion before opening the output
file. It does not perform an atomic file replacement.

The runtime requires software application metadata before plugin execution;
the direct [Python conversion API](api.md) only needs a parsed process and a
metadata prefix. A whole-document export is a plugin container, not an MCP
`tools/list` response. See [using definitions in MCP](../how-to/use-with-mcp.md).
