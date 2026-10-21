# Use definitions in an MCP server

Generate a selected Tool using the [runtime tutorial](../tutorials/first-steps.md).
An MCP server can then use that definition when advertising its tools. For a
whole-document export, take the values of the process-ID mapping first.
The plugin's JSON is not itself a protocol response.

The server is responsible for listing tools, handling calls, validating
arguments, executing the workflow, and returning results. See the
[MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
for the protocol messages and result contract.

Validate incoming arguments against the generated `inputSchema` and returned
objects against `outputSchema`. Enable a JSON Schema format checker if URI and
date-time formats should be enforced. The generated EOAP example expects scalar
URI and timestamp strings; an adapter must map them back to CWL record-shaped
values if its runner requires those records. The plugin supplies no execution
adapter.

Tool annotations describe intended behavior and do not grant authorization.
Discovery aliases in `_meta` do not register additional callable names.
See the [crosswalk](../reference/crosswalk.md) for the exact exported shapes.
