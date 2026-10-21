# Install cwl2mcp

Use Python 3.10 or newer. From this repository's root, install the plugin and its
runtime extra into the same environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install '.[cli]'
transpiler-mate cwl2mcp --help
```

For editable development, use `python -m pip install -e '.[cli,test]'` instead.
Dependencies are declared in [pyproject.toml](../../pyproject.toml); installation
normally requires network access.

The package installs a plugin entry point, not a standalone `cwl2mcp` executable.
`transpiler-mate-runtime` provides the `transpiler-mate` command.

Verify the registration and the imported source:

```sh
python -c "from cwl2mcp.plugin import cwl2mcp; print(cwl2mcp.name)"
python -c "import cwl2mcp; print(cwl2mcp.__file__)"
```

The first command prints `cwl2mcp`. If a traceback points to an older installed
copy, reinstall with the interpreter belonging to that CLI environment or use
an editable installation. Regenerating models in a checkout does not update a
separate installation automatically.

Continue with the [first tool tutorial](../tutorials/first-steps.md).
