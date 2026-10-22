# Configure output and metadata keys

From the repository root:

```sh
transpiler-mate cwl2mcp \
  --output build/tool.json \
  --meta-prefix org.example/mcp \
  tests/examples/eoap.cwl#main
```

`--output` defaults to `tools.json`. Missing parent directories are created;
existing files are replaced after successful conversion. JSON keys are sorted,
indentation is two spaces, and the file ends with a newline.

`--meta-prefix` defaults to `io.github.transpiler-mate/cwl2mcp`, users can customize it keeping in mind MCP’s `_meta` naming rules distinguish two parts:

| Part | Rules |
|---|---|
| Optional prefix, before `/` | Dot-separated labels; reverse DNS is recommended. Labels start with a letter, end with a letter or digit, and may contain internal hyphens. |
| Name, after `/` | May contain alphanumerics, hyphens, underscores, and dots. A nonempty name must start and end with an alphanumeric character. |

The command above
produces these custom keys when their values are nonempty:

- `org.example/mcp-aliases`
- `org.example/mcp-use-when`
- `org.example/mcp-do-not-use-when`

The suffixes use underscores. Empty lists and empty strings are omitted.

Use `tests/examples/eoap.cwl#main` to export one Tool. Omit `#main` to export an
object mapping process IDs to Tool definitions. This mapping is not an MCP
`tools/list` response.

For host integrations, construct `Cwl2McpOptions(output=Path("build/tool.json"),
meta_prefix="org.example/mcp")` and pass it to the plugin registration's
`execute(context, options)` method. See the [API reference](../reference/api.md)
and [crosswalk](../reference/crosswalk.md).
