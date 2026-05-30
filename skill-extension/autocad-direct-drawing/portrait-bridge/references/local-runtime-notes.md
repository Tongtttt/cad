# Local Runtime Notes

## Candidate local runtimes

### ComfyUI
- Root: your local ComfyUI installation
- Python venv: your ComfyUI Python environment
- Intended use: portrait segmentation and mask generation

### Node runtime
- Root: your local Node.js installation if you use orchestration scripts
- Intended use: helper CLIs and JSON transforms

## Current bridge scope

1. Define portrait semantic regions
2. Define region-to-layer mapping
3. Reserve script entry points for future segmentation execution
4. Keep CAD-side cleanup separate from recognition-side preprocessing
