# ComfyUI Integration

## Current result

The portrait bridge is designed to run through a local ComfyUI Python runtime and call the extractor script.

## Current limitation

- No dedicated portrait segmentation model/workflow is bundled here
- The extractor is designed to produce schema-shaped JSON and can be upgraded later with a stronger local workflow

## Why this is useful

- The runtime path is now explicit and configurable
- The recognition stage is separated from the CAD cleanup stage
- Future model integration only needs to replace the extractor internals, not the surrounding bridge contract
