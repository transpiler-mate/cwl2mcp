# cwl2mcp

[![PyPI - Version](https://img.shields.io/pypi/v/cwl2mcp.svg)](https://pypi.org/project/cwl2mcp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cwl2mcp.svg)](https://pypi.org/project/cwl2mcp)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/transpiler-mate/cwl2mcp/package.yaml?branch=develop&event=push&label=build&logo=githubactions)](https://github.com/transpiler-mate/cwl2mcp/actions/workflows/package.yaml?query=branch%3Adevelop)
[![Code coverage](https://img.shields.io/codecov/c/github/transpiler-mate/cwl2mcp/develop?logo=codecov)](https://app.codecov.io/gh/transpiler-mate/cwl2mcp/tree/develop)

A Transpiler Mate plugin deriving MCP tool definitions from parsed CWL v1.0–v1.2
processes. CWL is authoritative for value structure; EOAP `mcp:Tool` supplies
agent-facing metadata. This package does not execute CWL or run an MCP server.

## Installation and use

```bash
python -m pip install './cwl2mcp[cli]'
transpiler-mate cwl2mcp --output tool.json 'workflow.cwl#main'
transpiler-mate cwl2mcp --output tools.json workflow.cwl
```

The current runtime requires document-level schema.org application metadata
(name, description, dateCreated, license, softwareVersion, softwareHelp, publisher
and author) before invoking plugins. The complete example and graph fixture show
this metadata. The Python API does not require it.

The runtime resolves imports and selects processes. A `#process` selection writes
one MCP Tool object. Without a fragment, output is an object mapping the runtime's
process IDs to tool definitions, including workflows, CommandLineTools and
ExpressionTools. This mapping is an export container, not an MCP `tools/list`
response. JSON keys are sorted, output ends with a newline, and parent directories
are created. Conversion completes before an existing file is overwritten.

```python
from cwl_utils.parser import load_document_by_uri
from cwl2mcp.converter import to_mcp_tool

process = load_document_by_uri('file:///absolute/path/workflow.cwl')
# Select one process first if the loader returned a list.
tool = to_mcp_tool(process)
print(tool.model_dump_json(by_alias=True, exclude_none=True, indent=2))
```

## Documentation

The documentation follows Diátaxis and is published at
<https://Transpiler-Mate.github.io/cwl2oci/>:

- tutorials for guided learning;
- how-to guides for specific tasks;
- reference for the exact plugin and output contracts;
- explanation for architecture and design context.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Submit issues at
<https://github.com/Transpiler-Mate/cwl2oci/issues>.

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
