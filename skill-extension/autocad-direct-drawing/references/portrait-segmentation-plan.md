# Portrait Segmentation Plan

## Goal

Add a smart portrait-recognition layer above the current CAD LISP cleanup workflow so that portrait line art can be grouped by semantic region before connect/smooth operations.

## Target semantic regions

- hand
- flower
- main hair mass
- fine hair detail
- facial features
- clothing
- ornaments
- outer silhouette

## Current state

- CAD-side cleanup exists: layer creation, grouped movement, connect, smooth
- True semantic recognition is not yet available locally
- Current best fallback is grouped manual assignment into Chinese portrait layers

## Planned architecture

1. Input reference image
2. External segmentation or region-detection step
3. Region-to-layer mapping output
4. CAD-side import or assignment helper
5. Local connect/smooth refinement

## Integration rule

When a usable local or remote segmentation capability becomes available, integrate it as a pre-processing stage for `autocad-direct-drawing` instead of replacing the existing CAD cleanup commands.

## Fallback rule

If semantic segmentation is unavailable, fall back to:
1. `PORTRAITLAYERS`
2. `LAYERGROUP`
3. `CCONNECT`
4. `CSMOOTH`
