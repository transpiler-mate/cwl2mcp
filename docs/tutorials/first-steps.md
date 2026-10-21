# Generate your first MCP Tool definition

[Install the plugin and runtime](../how-to/install.md), then run the commands
below from this repository's root. The [EOAP example](../../tests/examples/eoap.cwl)
includes the software application metadata required by the runtime and a complete
MCP hint. Its remote schema imports require network access or a populated loader
cache.

## Export one process

```sh
transpiler-mate cwl2mcp --output build/tool.json tests/examples/eoap.cwl#main
python -m json.tool build/tool.json
```

The file contains one Tool with `name` equal to `inspect_source`, `title` equal to
`Inspect Source`, and `inputSchema`, `outputSchema`, `annotations`, and `_meta`.
The description comes from the CWL `doc`; selection guidance is in `_meta`.

## Export the document

```sh
transpiler-mate cwl2mcp --output build/tools.json tests/examples/eoap.cwl
```

This produces a mapping with a `main` entry containing the Tool definition.
Neither command executes the expression in the CWL document.

## Inspect the argument contract

The generated input schema accepts this shape:

```json
{
  "source": "https://example.org/data.tif",
  "timestamp": "2026-10-18T06:00:00Z",
  "point": {
    "type": "Point",
    "coordinates": [12.5, 41.9],
    "bbox": [12.5, 41.9, 12.5, 41.9]
  }
}
```

The source [CWL arguments fixture](../../tests/examples/arguments.json) uses
`{"value": ...}` records for URI and DateTime. Those wrappers are flattened by
the current schema converter, so that fixture is not a valid MCP argument object
without adaptation. The output schema similarly uses scalar `source_result`
and `timestamp_result` fields and a structured `point_result` field.

Read the [crosswalk](../reference/crosswalk.md) for current mappings, or
[configure the destination and metadata prefix](../how-to/configure-output.md).
