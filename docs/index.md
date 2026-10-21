# CWL to MCP

`cwl2mcp` converts parsed CWL processes into MCP Tool definitions and writes them
as JSON through `transpiler-mate-runtime`. It does not execute CWL or start an
MCP server.

## Start here

- [Install the plugin and runtime](how-to/install.md).
- [Generate your first tool definition](tutorials/first-steps.md).
- [Configure output and metadata keys](how-to/configure-output.md).
- [Use the exported definitions in an MCP server](how-to/use-with-mcp.md).
- Look up the [CWL-to-MCP crosswalk](reference/crosswalk.md),
  [Python and plugin API](reference/api.md), and
  [generated hint reference](reference/hints_schema.html).
- Read about the [architecture](explanation/architecture.md).

Python 3.10 or newer is required. The runtime discovers the installed plugin via
its `transpiler_mate.plugins` entry point. See the
[project configuration](../pyproject.toml) for dependencies and quality checks.
