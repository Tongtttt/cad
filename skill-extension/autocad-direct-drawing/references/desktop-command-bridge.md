# Desktop Command Bridge

## Purpose

This bridge targets the visible AutoCAD desktop window and injects commands through Windows SendKeys.

## Helper script

- `scripts/send_visible_autocad_keys.ps1`

## Why this exists

COM can attach to a hidden automation instance instead of the visible desktop drawing.
The desktop bridge is the fallback path for the actual user-facing AutoCAD session.

## Use sequence

1. Verify the visible AutoCAD title
2. Compare it with the COM document name
3. If they differ, prefer the desktop command bridge
