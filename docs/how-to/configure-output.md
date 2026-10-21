# Configure output and metadata keys

From the repository root:

```sh
transpiler-mate cwl2mcp \
  --output build/tool.json \
  --meta-prefix example.org/mcp \
  tests/examples/eoap.cwl#main
```

`--output` defaults to `tools.json`. Missing parent directories are created;
existing files are replaced after successful conversion. JSON keys are sorted,
indentation is two spaces, and the file ends with a newline.

`--meta-prefix` defaults to `transpiler-mate.github.io/cwl2mcp`. The command above
produces these custom keys when their values are nonempty:

- `example.org/mcp-aliases`
- `example.org/mcp-use_when`
- `example.org/mcp-do_not_use_when`

The suffixes use underscores. Empty lists and empty strings are omitted.

Use `tests/examples/eoap.cwl#main` to export one Tool. Omit `#main` to export an
object mapping process IDs to Tool definitions. This mapping is not an MCP
`tools/list` response.

For host integrations, construct `Cwl2McpOptions(output=Path("build/tool.json"),
meta_prefix="example.org/mcp")` and pass it to the plugin registration's
`execute(context, options)` method. See the [API reference](../reference/api.md)
and [crosswalk](../reference/crosswalk.md).
