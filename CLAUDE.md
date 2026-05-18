# CLAUDE.md

AutoCAD MCP server — bridges Claude AI with AutoCAD LT via the Model Context Protocol (Python).

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                          # Install dependencies
uv run pytest tests/ -v          # Run all tests
uv run pytest tests/test_ezdxf_backend.py -v  # Run ezdxf backend tests
uv run pytest tests/test_ipc_protocol.py -v   # Run IPC protocol tests
uv run python -m autocad_mcp     # Run MCP server manually
```

## Architecture

```
MCP Client (Claude)
    │  stdio (JSON-RPC)
    ▼
autocad_mcp/server.py          — FastMCP server, 8 tools with operation dispatch
    │
    ├── backends/file_ipc.py   — File IPC: PostMessageW(WM_CHAR) → mcp_dispatch.lsp in AutoCAD LT
    │   Reads/writes JSON via C:/temp/*.json, no focus steal
    │
    └── backends/ezdxf_backend.py — Headless DXF generation, no AutoCAD required
        Uses ezdxf + matplotlib for rendering
```

- **`src/autocad_mcp/server.py`** — All 8 MCP tools (`drawing`, `entity`, `layer`, `block`, `annotation`, `pid`, `view`, `system`). Each tool dispatches operations to the active backend. Tools return `str | list` (list for ImageContent + TextContent).
- **`src/autocad_mcp/client.py`** — Backend auto-detection (`auto` → try file_ipc, fallback ezdxf), error wrapping (`_safe`, `_error`, `_json`), screenshot helper.
- **`src/autocad_mcp/config.py`** — Environment variable parsing (`AUTOCAD_MCP_BACKEND`, `AUTOCAD_MCP_IPC_DIR`, etc.).
- **`src/autocad_mcp/screenshot.py`** — Win32 PrintWindow for File IPC, matplotlib render for ezdxf.
- **`src/autocad_mcp/pid/cto_library.py`** — CTO P&ID symbol library mapping.
- **`lisp-code/mcp_dispatch.lsp`** — AutoLISP dispatcher loaded in AutoCAD LT 2024+. Reads IPC JSON, executes commands, writes results back.
- **`tests/`** — Pytest with `asyncio_mode = "auto"`. Tests cover ezdxf backend and IPC protocol.

## Backend Selection

Set `AUTOCAD_MCP_BACKEND` env var: `auto` (default, tries File IPC first), `file_ipc` (requires AutoCAD LT 2024+ Windows), `ezdxf` (headless, cross-platform).

## Key Constraints

- File IPC backend requires Windows native Python (not WSL) — uses `pywin32` for `PostMessageW`.
- When running from WSL, launch via `cmd.exe /d /s /c` so Python runs as native Windows process.
- LISP files use Windows-1252 encoding; Python side has UTF-8/cp1252 fallback for result parsing.
