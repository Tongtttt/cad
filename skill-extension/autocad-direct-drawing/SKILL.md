---
name: "autocad-direct-drawing"
description: "Use when the user wants to work with AutoCAD on Windows: connect to an open drawing, drive AutoCAD via COM or MCP, load AutoLISP helpers, import vector/JSON linework, or troubleshoot why direct automation cannot see the active AutoCAD window."
---

# AutoCAD Direct Drawing

Use this skill for Windows AutoCAD work where Codex should operate on a real drawing instead of only describing steps.

## When to use

- User mentions `AutoCAD`, `CAD`, `DWG`, `LISP`, `APPLOAD`, or a currently open drawing
- User wants Codex to draw/import geometry into AutoCAD
- User wants to automate an existing AutoCAD session via COM or MCP
- User wants to convert local image/vector data into editable CAD linework
- User says AutoCAD automation cannot find the active window or drawing

## Core behavior

1. Prefer direct execution over teaching.
2. Prefer connecting to the user's active visible AutoCAD desktop session.
3. Assume the user may have opened AutoCAD and the target DWG in advance; prefer that visible instance over background automation instances.
4. If direct connection is blocked, diagnose the blocker before proposing fixes.
5. If direct drawing is not immediately possible, generate a usable fallback artifact such as `.lsp`, `.scr`, JSON linework, or a PowerShell bridge.

## Workflow

### 1. Establish the control path

Try these in order:

1. Existing MCP bridge for AutoCAD
2. Native AutoCAD COM automation on Windows
3. AutoLISP / script-file fallback loaded into AutoCAD

Choose the first path that can actually draw into the current DWG.

### 2. Confirm live AutoCAD state

Check:

- Is `acad.exe` running?
- Is there an open drawing, not just the welcome screen?
- Is AutoCAD running under a different privilege level or desktop session?
- Can COM see `AutoCAD.Application.*`?
- Does COM point to the same visible DWG the user opened on the desktop?
- Is COM accidentally attached to a hidden automation instance instead of the visible drawing window?

If AutoCAD is visible to the user but invisible to automation, suspect permission or session isolation first.
If COM resolves to a hidden automation instance, do not modify that document as if it were the user's visible drawing.

### 3. Prefer useful output over stalled debugging

If a direct bridge is flaky, do not stop at “connection failed”. Produce a fallback the user can run immediately:

- `AutoLISP` for `APPLOAD`
- `.scr` command script
- JSON/polyline export for later import
- PowerShell bridge that reads prepared geometry and writes into `ModelSpace`

### 4. Geometry strategy

- If the source is already vector or structured coordinates, keep it vector.
- If the source is raster, extract the minimum editable linework needed for the task.
- Preserve layers and closed polylines when possible.
- Name layers explicitly and keep output reusable.

### 5. Verification

Before claiming success, verify one of these:

- COM reports new entities in `ModelSpace`
- AutoCAD accepted and executed the generated script
- The generated fallback file exists and is ready for the user to load
- The document being modified matches the visible DWG the user opened

## Troubleshooting priorities

### AutoCAD cannot be found

Likely causes:

- AutoCAD launched as administrator while Codex is not
- AutoCAD is on a different Windows session/desktop
- No drawing is actually open
- The detected COM ProgID version is wrong

### COM found the wrong drawing

Likely causes:

- COM attached to a hidden automation instance
- Multiple `acad.exe` instances are running
- Hidden automation session exists alongside the visible desktop session

Recovery order:

1. Identify visible vs hidden instances
2. Prefer the visible desktop drawing the user opened manually
3. Avoid editing `Drawing1.dwg` in a hidden automation instance unless the user explicitly asked for it
4. If switching cannot be made reliable, fall back to a loadable artifact for the visible DWG

### Script sent but nothing appears

Check:

- Was the command terminated correctly?
- Did AutoCAD prompt for input mid-command?
- Did entities land far from origin?
- Is the drawing on the expected layer and viewport?

### Image-to-CAD quality is poor

Adjust in this order:

1. Source quality / thresholding
2. Number of contours kept
3. Polyline simplification amount
4. Layer separation

## Deliverables

Return the smallest artifact that gets the user moving:

- direct AutoCAD changes when possible
- otherwise a clickable local file path to the generated `.lsp`, `.scr`, `.ps1`, or JSON artifact

## Local notes

- If local AutoCAD helper scripts or MCP servers already exist, reuse them before inventing a new bridge.
- Keep generated helper files inside the active workspace unless the user explicitly asks for a global install.
- For repeated local workflows, prefer saving a reusable bridge script instead of retyping commands each session.
- In this environment, expect the user to pre-open the target AutoCAD drawing on the desktop; treat that visible drawing as the primary target.

For diagnostic command patterns and fallback guidance, read `references/troubleshooting.md` when needed.

## Persistent local workflow

Read `references/persistent-workflow.md` for this machine's fixed AutoCAD connection policy and fallback paths.

## Local bridge scripts

Use these local scripts before blind COM edits on this machine:

- `scripts/detect_visible_autocad.ps1` to identify the visible AutoCAD desktop window and distinguish it from automation instances
- `scripts/generate_cad_script.ps1` to create a stable `.scr` fallback for the visible drawing

Read `references/local-bridge-notes.md` when future sessions need the fixed local bridge policy.

## Smoothing existing linework

When the user already traced a drawing in CAD and only wants cleaner, smoother lines:

1. Prefer operating on the existing CAD entities instead of re-vectorizing the reference image.
2. Generate a reusable `.lsp` helper if direct entity editing is not yet safely automated.
3. Optimize for portrait linework with hair strands, floral contours, sleeves, and hand outlines.
4. Keep the first pass conservative: improve flow without destroying silhouette intent.

## Connecting broken portrait segments

When portrait linework contains many short broken segments:

1. Do not only smooth; connect first where the contour is obviously meant to be continuous.
2. Prefer conservative join distance and smaller local selections for hair, eyelashes, petals, jewelry, and fingers.
3. Run a connect pass first, then a smoothing pass.
4. Avoid globally joining everything, because decorative detail can collapse if the fuzz distance is too large.

## Layer-first portrait cleanup

For portrait line art based on a reference image, separate major structures into layers before smoothing or joining.

Recommended logical groups:
- outer silhouette
- main hair masses
- fine hair/detail strands
- facial features
- hands
- clothing
- main flowers
- flower inner detail
- ornaments and jewelry
- leftover misc detail

Reason: layer-first cleanup reduces accidental joins across unrelated features and makes local retries safer.

## Semi-automatic portrait layer assignment

When the user wants portrait linework grouped before cleanup:

1. Create the standard portrait layers first.
2. Prefer grouped user selection into predefined portrait layers over unreliable blind spatial guessing when entity assignment must be trustworthy.
3. Treat the result as a first pass only; require quick human review before connection and smoothing.
4. Prefer this over globally editing all entities in one layer.

## Portrait semantic segmentation

For complex portrait drawings where hands, flowers, hair, ornaments, and clothing overlap, pure LISP selection is not enough.

Treat semantic portrait segmentation as an optional pre-processing layer above CAD cleanup:

1. Try semantic region recognition when available
2. Map recognized regions into portrait layers
3. Use CAD cleanup tools only after regional grouping is in place
4. Fall back to grouped manual assignment when segmentation is unavailable

Read `references/portrait-segmentation-plan.md` when working on smarter portrait grouping or future GitHub/model integrations.

## Desktop command bridge

If COM attaches to the wrong AutoCAD document but the visible desktop window is correct, use the local desktop command bridge instead of pretending COM is safe.

Read `references/desktop-command-bridge.md` and prefer `scripts/send_visible_autocad_keys.ps1` when direct command injection into the visible AutoCAD session is needed.

## Portrait bridge module

Use `portrait-bridge/` as the local integration point for portrait recognition and CAD entity-selection assistance.

- `portrait-bridge/references/local-runtime-notes.md` tracks available local runtimes
- `portrait-bridge/references/portrait_regions.schema.json` defines the region output contract
- `portrait-bridge/scripts/run_comfyui_portrait_bridge.ps1` is the stable local entry point
- `portrait-bridge/scripts/portrait_region_extractor.py` generates semantic portrait regions through a local Python runtime
- Current first-choice backend: local `torchvision` Mask R-CNN person segmentation; fallback: deterministic line-art heuristic grouping

## Visible COM Recovery

On Windows, `New-Object -ComObject AutoCAD.Application.*` may attach to a hidden automation instance even when the visible DWG is already open.

Use this recovery order:

1. Detect the visible AutoCAD desktop window first
2. Prefer `[System.Runtime.InteropServices.Marshal]::GetActiveObject('AutoCAD.Application.*')` over `New-Object -ComObject` when the visible session is already open
3. If `ActiveDocument` looks empty at first, retry and re-activate the visible document before assuming COM failed
4. Once `ActiveDocument.Name`, `FullName`, and `ModelSpace.Count` are non-empty, prefer direct COM entity processing over SendKeys

## Current Practical Boundary

This skill can now do all of the following when the local bridge is configured:

- detect the visible DWG window
- attach COM to the real visible AutoCAD instance
- export entity geometry from the visible DWG
- run semantic portrait region grouping and map those regions into CAD layers
- recolor and reorganize entities through COM

This skill still does **not** have a fully reliable non-interactive bridge for AutoCAD's interactive `PEDIT/JOIN/SMOOTH` command chain.
When the user asks for fully automatic final smoothing, treat SendKeys-based command injection as best-effort only and document that risk explicitly.

## Project Mode Split

Use two different working modes in this skill:

### 1. Portrait / character tracing mode

Use this mode only when the user clearly says they are drawing a person, anime character, portrait, or tracing a character image.

Rules:
- This mode is mainly for entertainment / visual likeness
- The goal is to trace or approximate the reference image according to the user's requested style
- Keep all existing portrait-related bridges, segmentation work, layer grouping logic, and AutoCAD helper workflows active
- Precision matters, but engineering manufacturing correctness is not the primary standard

### 2. Engineering / chemical drafting mode

Use this mode by default unless the user explicitly indicates portrait/character tracing.

Rules:
- This mode is the default for ambiguous CAD requests
- Treat the task as engineering drafting first, especially for mechanical / chemical / piping / valve / equipment drawings
- Prioritize dimensional logic, standards, structure, constraints, annotation meaning, and drawing correctness over visual similarity
- Do not rely on image-like approximation when the task is really an engineering drawing
- If the user does not explicitly say the target is a person or a character image, assume they want rigorous engineering drafting
