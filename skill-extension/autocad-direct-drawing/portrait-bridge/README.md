# Portrait Bridge

Local bridge for portrait-region recognition and AutoCAD entity selection.

## Purpose

This module sits between reference image understanding and CAD entity grouping/selection.
It prepares structured region data that the CAD-side tools can consume.

## Runtime

- Entry script: `scripts/run_comfyui_portrait_bridge.ps1`
- Python runtime: set `COMFYUI_PYTHON` to your local ComfyUI Python executable
- Extractor: `scripts/portrait_region_extractor.py`

## Behavior

1. Try local `torchvision` Mask R-CNN person segmentation first
2. If that is unavailable, fall back to a deterministic line-art heuristic segmenter
3. Output schema-shaped `portrait_regions.json` with regions such as hair, face, hand, cloth, flower, ornament, and misc

## Output contract

See `references/portrait_regions.schema.json`.

## Notes

- The JSON contract is stable and can be consumed by CAD-side scripts.
- The extractor is designed to be replaceable with a stronger local workflow or custom node later.
