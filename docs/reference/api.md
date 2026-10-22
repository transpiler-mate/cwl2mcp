# Plugin and Python API

## Registration and options

The [plugin implementation](../../src/cwl2mcp/plugin.py) registers
`cwl2mcp.plugin:cwl2mcp` as `cwl2mcp` in the `transpiler_mate.plugins` group.
The decorated object is a plugin registration; a host invokes
`cwl2mcp.execute(context, options)`.

`Cwl2McpOptions` rejects unknown fields:

| Option | Python type | Default |
|---|---|---|
| `output` | `pathlib.Path` | `tools.json` |
| `meta_prefix` | `str` | `io.github.transpiler-mate/cwl2mcp` |

The runtime exposes these as `--output` and `--meta-prefix`. See
[output configuration](../how-to/configure-output.md).

When `context.process_id` is set, the plugin converts `context.resolved_process`.
Otherwise it converts each process in `context.document` and writes a mapping
keyed by the runtime's process IDs. The runtime also prepares software application
metadata, but this plugin reads tool metadata from the CWL process and hint.

## Direct conversion

```python
from pathlib import Path
from cwl_utils.parser import Process, load_document_by_uri
from cwl2mcp.converter import to_mcp_tool

process = load_document_by_uri(
    Path("tests/examples/eoap.cwl").resolve().as_uri() + "#main"
)
assert isinstance(process, Process)
tool = to_mcp_tool(process, meta_prefix="example.org/mcp")
payload = tool.model_dump(by_alias=True, exclude_none=True)
```

`to_mcp_tool(process, meta_prefix)` returns the generated `McpTool` Pydantic model
and does not write files. `meta_prefix` is required in the Python API.
`get_tool_hint(process)` in [converter.py](../../src/cwl2mcp/converter.py) returns
the first matching `Tool` hint, or `None`. It accepts parsed hints and validates
mapping hints using the generated Salad model.

## Errors

- Malformed hint mappings raise Schema Salad `ValidationException`.
- Invalid tool fields raise Pydantic `ValidationError` during conversion.
- Schema conversion can raise errors from `cwl2ogc`.
- The plugin wraps conversion-time `ValueError` as `PluginFailureError`.
  Salad validation errors are not wrapped by that handler.
- File-system `OSError` is wrapped as `PluginExecutionError`.

Conversion finishes before the destination is opened. Parent directories are
created. Writing is not an atomic replacement: an I/O failure after opening can
leave a partial file. See the [crosswalk](crosswalk.md) for serialization details.
