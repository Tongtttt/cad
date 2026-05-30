# Portrait Automation Progress

## Scope

This note records the current portrait automation workflow for CAD cleanup.

## What is available

1. Local portrait semantic segmentation pipeline
- `portrait-bridge/scripts/portrait_region_extractor.py` produces `portrait_regions.json`
- segmentation uses a local `torchvision` person segmentation path plus rule-based region partitioning when possible

2. Visible AutoCAD detection
- `scripts/detect_visible_autocad.ps1` can find the visible desktop AutoCAD window and DWG title

3. Visible COM recovery
- `Marshal.GetActiveObject('AutoCAD.Application.*')` may attach to the real visible AutoCAD session when available

4. Entity-level CAD automation
- entity geometry can be exported from the visible DWG via COM
- semantic region mapping can be projected into the DWG coordinate space
- entities can be reassigned to portrait cleanup layers through COM or script fallback

## What remains best-effort

1. SendKeys command injection
- useful as a fallback, but not deterministic for all interactive commands

2. Fully automatic smoothing
- interactive cleanup chains still need a reliable non-interactive path

## Current best practice

1. User opens the real DWG in visible desktop AutoCAD
2. Recover the visible AutoCAD COM object
3. Export entity geometry through COM
4. Run portrait semantic grouping and layer reassignment
5. Use SendKeys only as a fallback for interactive cleanup commands
