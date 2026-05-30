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
