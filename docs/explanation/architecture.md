# Architecture and data flow

```text
transpiler-mate-runtime
  resolves CWL, prepares metadata, selects processes, validates options
        |
        v
cwl2mcp plugin
  loads the first matching Tool hint
  delegates input/output schema conversion to cwl2ogc
  constructs a generated McpTool model
  serializes one Tool or a process-ID mapping
        |
        v
tools.json
```

The runtime owns document loading and plugin discovery. The
[plugin](../../src/cwl2mcp/plugin.py) writes JSON; the
[converter](../../src/cwl2mcp/converter.py) returns a Tool without performing file
I/O. An [MCP server](../how-to/use-with-mcp.md) must supply execution and protocol
handling separately.

## Two schema boundaries

[schemas/hints.yaml](../../schemas/hints.yaml) is a Schema Salad extension of
CWL. Its generated [mcp_hint.py](../../src/cwl2mcp/mcp_hint.py) validates custom
hint mappings. Imported CWL and Salad classes are reused from `cwl-utils` and
`schema-salad`. The generator uses `Any` constructor annotations; validation
occurs in `fromDoc()`, not in those annotations.

[schemas/mcp-tool.yaml](../../schemas/mcp-tool.yaml) defines the project's MCP
Tool authoring profile. Its generated [mcp_tool.py](../../src/cwl2mcp/mcp_tool.py)
contains Pydantic models. This profile is distinct from the official protocol
schema. Constructing `McpTool` validates model fields but does not execute the
embedded JSON Schemas against arguments or results.

The converter preserves the literal hint name after Salad validation because
Salad's shared `name` predicate otherwise applies document-relative identifier
expansion. Input/output schema conversion uses the pinned `cwl2ogc` dependency;
its generated schemas are copied without a separate artifact-receipt layer.

## Regeneration

Run the configured tasks from the repository root:

```sh
task generate_mpc_hint
task generate_mpc_tool
task generate_schema_doc
```

The `mpc` spelling is the current task name. The Tool task invokes the shared
Terradue `json:create_models` task; the hint tasks use Schema Salad. See
[Taskfile.yaml](../../Taskfile.yaml). Change source schemas and regenerate rather
than editing generated classes or the [HTML hint reference](../reference/hints_schema.html).

## Verification

[Runtime integration tests](../../tests/test_runtime_crosswalk.py) exercise real
CLI discovery and exported JSON. Assertions cover the current scalar URI/DateTime projection, metadata keys,
selected-process and document exports, and deterministic serialization. The
[hint schema tests](../../tests/test_hint_schema.py) cover the title and nested
annotation handling. Run `task quality:pre-commit:run` for the complete quality gate. The test
environments install JSON Schema format validators so malformed URI and
date-time values are rejected.

The hint-generation task applies reviewed Ruff rewrites and formatting after
code generation. Generated loader complexity and schema-shaped signatures have
file-specific Ruff exceptions; the upstream abstract-loader registration has a
narrow mypy exception. Other checks remain enabled. See the comments in
[pyproject.toml](../../pyproject.toml) for these generated-code boundaries.
