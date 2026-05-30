# CLAUDE.md

AutoCAD MCP server - bridges Claude AI with AutoCAD LT via the Model Context Protocol (Python).

This repository contains the core AutoCAD MCP server plus a portable local skill extension for visible AutoCAD workflows.

## Commands

```bash
uv sync
uv run pytest tests/ -v
uv run pytest tests/test_ezdxf_backend.py -v
uv run pytest tests/test_ipc_protocol.py -v
uv run python -m autocad_mcp
```

## Notes

- Use the visible AutoCAD session when available.
- Keep machine-specific paths in local configuration or environment variables.
- The `skill-extension/autocad-direct-drawing/` folder contains the local skill bundle.
