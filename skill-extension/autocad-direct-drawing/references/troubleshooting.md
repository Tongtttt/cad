# Troubleshooting Reference

## Fast checks

- Confirm `acad.exe` is running.
- Confirm an actual drawing is open.
- Check whether AutoCAD is elevated while Codex is not.
- Check whether COM can see `AutoCAD.Application.*`.
- Check whether COM points to the visible desktop DWG or only to a hidden automation instance.

## Preferred recovery order

1. Retry with the correct privilege/session alignment.
2. Distinguish visible desktop AutoCAD from hidden `/Automation -Embedding` instances.
3. Prefer the visible drawing the user opened manually.
4. Try an AutoCAD MCP bridge if present.
5. Fall back to a generated `.lsp` or `.scr`.
6. If needed, generate a PowerShell COM bridge that writes geometry directly.

## Wrong-instance warning

Do not assume the first COM-visible `Drawing1.dwg` is the user's real target.
When multiple `acad.exe` processes exist, verify whether the visible desktop drawing and the COM-attached drawing are the same before editing.

## Good fallback artifacts

- `drawing_import.lsp`
- `draw_geometry.scr`
- `import_geometry.ps1`
- `geometry.json`

## P&ID-specific

### Symbol not found
- Run `pid(operation="list_symbols", data={"category": "VALVES"})` (or other category) to see available symbols.
- Verify `CTO_ROOT` is `C:/PIDv4-CTO` and the `.dwg` file exists at that path.
- Symbol filenames match the `cto_library.py` catalog entries — check `C:\Users\ASUS\cad\src\autocad_mcp\pid\cto_library.py` for the full list.

### Attribute prompt blocking insertion
- `attribute_tools.lsp` sets `ATTREQ=0` to suppress attribute dialogs during batch insertion.
- If AutoCAD still shows an attribute prompt, press ESC and reload the LISP: `(load "attribute_tools.lsp")`.

### Layer not created
- Run `pid(operation="setup_layers")` as the first step for any new P&ID drawing.
- The standard layers are: PID-EQUIPMENT, PID-PROCESS-PIPING, PID-UTILITY-PIPING, PID-INSTRUMENTS, PID-ELECTRICAL, PID-ANNOTATION, PID-VALVES.

### Headless mode producing simplified symbols
- The ezdxf backend produces labeled geometric placeholders (rectangles for equipment, diamonds for valves, circles for instruments) rather than true ISA 5.1 symbol blocks.
- This is expected behavior. Open the generated `.dxf` in live AutoCAD and re-insert symbols from CTO library for production-quality output.
- For production P&IDs, prefer the `file_ipc` backend with live AutoCAD.

### Wrong document / hidden instance (P&ID context)
- Same COM hidden-instance rules apply. See "Wrong-instance warning" above.
- After killing hidden acad.exe instances, re-verify with `drawing(operation="info")` from MCP.
