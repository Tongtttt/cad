# Local Bridge Notes

## Bridge strategy

Do not trust the first COM-visible AutoCAD document by default.
Use local window detection first to identify the visible AutoCAD window and its DWG title.

## Preferred sequence

1. Detect visible AutoCAD window title with `detect_visible_autocad.ps1`
2. Compare visible DWG title with COM-attached document name
3. If they differ, avoid blind COM edits
4. Generate a script artifact targeted at the visible drawing instead

## Scripts

- `scripts/detect_visible_autocad.ps1`
- `scripts/generate_cad_script.ps1`
