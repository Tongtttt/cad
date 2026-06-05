# Persistent Workflow

## Default behavior

1. Open the target DWG manually in visible desktop AutoCAD first.
2. Bind to the visible instance, not a hidden automation session.
3. If COM resolves to the wrong document, avoid blind edits and generate a loadable helper artifact instead.
4. Prefer reusable `.scr`, `.lsp`, or PowerShell bridge scripts for repeated work.

## Stable paths

- Skill root: the installed `autocad-direct-drawing` skill directory
- Helper scripts: the skill `scripts/` directory
- References: the skill `references/` directory

## Rule for future sessions

When the user says they already opened CAD on the desktop, assume the visible drawing is the source of truth.
Do not trust `Drawing1.dwg` from COM unless it matches the visible DWG name.
If they do not match, switch to a generated helper artifact rather than pretending the COM target is correct.

## Reusable helpers

- `scripts/send_visible_autocad_keys.ps1` for visible AutoCAD command injection
- `scripts/generate_cad_script.ps1` for stable `.scr` output

## Portrait cleanup helpers

Use the portrait cleanup workflow only when the user clearly requests portrait or character tracing.
For engineering drawings, default to rigorous drafting behavior.

## Default CAD intent rule

- If the user explicitly says they are drawing a person, portrait, anime character, or tracing a character image, use portrait tracing mode
- Portrait tracing mode is for entertainment / likeness work and may use the existing portrait automation stack
- If the user does not clearly say the target is a person or character image, default to engineering / chemical drafting mode
- Engineering / chemical drafting mode must be treated as rigorous drafting work, not freehand likeness reconstruction
- For P&ID and chemical drafting specifically, prefer the AutoCAD MCP Server `pid` tool at `C:\Users\ASUS\cad\` over raw COM calls
- When MCP is unavailable, fall back to LISP helpers from `C:\Users\ASUS\cad\lisp-code\attribute_tools.lsp`
- The MCP server `.mcp.json` at `C:\Users\ASUS\cad\.mcp.json` defines the bridge configuration
